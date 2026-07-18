import os
import sys
import uuid
from collections import Counter
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload


_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from ai_engine import agents, rag  # noqa: E402

from app.models import Bookmark, Chapter, ChapterStatus, Novel, NovelGenre, NovelStatus, ReadingHistory, User
from app.services import chapter_service

MIN_SUMMARY_SOURCE_CHARS = 200


def _accessible_chapters(db: Session, novel: Novel, viewer: Optional[User]) -> List[Chapter]:
    """Return the list of chapters the viewer is allowed to read."""
    published = (
        db.query(Chapter)
        .filter(Chapter.novel_id == novel.id, Chapter.status == ChapterStatus.PUBLISHED)
        .order_by(Chapter.chapter_number.asc())
        .all()
    )

    is_owner_or_admin = viewer is not None and (
        viewer.id == novel.author_id or viewer.role.value == "ADMIN"
    )
    if is_owner_or_admin:
        return published

    accessible = []
    for chapter in published:
        if not chapter.is_premium:
            accessible.append(chapter)
        elif viewer is not None and chapter_service.user_has_purchased_chapter(db, viewer, chapter):
            accessible.append(chapter)
    return accessible


# Story Summary
def generate_novel_summary(db: Session, novel: Novel, viewer: Optional[User]):
    """Generate a spoiler-light summary from the chapters the viewer can access."""
    accessible = _accessible_chapters(db, novel, viewer)

    combined_text = "\n\n".join(ch.content for ch in accessible)[:6000]
    if len(combined_text) < MIN_SUMMARY_SOURCE_CHARS:
        combined_text = (novel.description or "") + "\n\n" + combined_text

    if not combined_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough published content available yet to generate a summary",
        )

    result = agents.run_summary(novel.title, combined_text)
    return result["summary"]



# RAG indexing + Q&A
def reindex_novel(db: Session, novel: Novel) -> int:
    """Re-index all published chapters of a novel for RAG retrieval."""
    chapters = (
        db.query(Chapter)
        .filter(Chapter.novel_id == novel.id, Chapter.status == ChapterStatus.PUBLISHED)
        .order_by(Chapter.chapter_number.asc())
        .all()
    )
    chapter_inputs = [
        {
            "chapter_id": str(ch.id),
            "chapter_number": ch.chapter_number,
            "chapter_title": ch.title,
            "content": ch.content,
        }
        for ch in chapters
    ]
    return rag.index_novel_chapters(novel.id, chapter_inputs)


def answer_question_about_novel(db: Session, novel: Novel, viewer: User, question: str):
    """Answer a question about a novel using RAG retrieval and LLM generation."""
    from ai_engine import llm as ai_llm
    from ai_engine.prompts import QA_SYSTEM_PROMPT, build_qa_prompt

    accessible_ids = {str(ch.id) for ch in _accessible_chapters(db, novel, viewer)}

    # Over-fetch, since some of the top matches may turn out to be locked.
    retrieved_chunks = rag.retrieve_relevant_chunks(novel.id, question, top_k=15)
    allowed_chunks = [
        c for c in retrieved_chunks if c["metadata"]["chapter_id"] in accessible_ids
    ][:8]

    documents = [c["document"] for c in allowed_chunks]
    prompt = build_qa_prompt(question, documents)
    answer = ai_llm.generate(prompt, system=QA_SYSTEM_PROMPT, temperature=0.2)

    sources = [
        {
            "chapter_id": uuid.UUID(c["metadata"]["chapter_id"]),
            "chapter_number": c["metadata"]["chapter_number"],
            "chapter_title": c["metadata"]["chapter_title"],
            "snippet": c["document"][:200],
        }
        for c in allowed_chunks
    ]

    return answer, sources

# Personalized recommendations (genre-based)
def get_recommendations_for_user(db: Session, user: User, limit: int = 10) -> List[Novel]:
    """Return a list of recommended novels for a user based on their reading history and bookmarks."""
    liked_novel_ids = {
        b.novel_id
        for b in db.query(Bookmark.novel_id).filter(Bookmark.user_id == user.id).all()
    }
    read_novel_ids = {
        h.novel_id
        for h in db.query(ReadingHistory.novel_id).filter(ReadingHistory.user_id == user.id).all()
    }
    engaged_novel_ids = liked_novel_ids | read_novel_ids

    genre_ids: List[uuid.UUID] = []
    if engaged_novel_ids:
        genre_rows = (
            db.query(NovelGenre.genre_id)
            .filter(NovelGenre.novel_id.in_(engaged_novel_ids))
            .all()
        )
        genre_counts = Counter(row[0] for row in genre_rows)
        genre_ids = [genre_id for genre_id, _ in genre_counts.most_common(5)]

    base_query = db.query(Novel).options(
        joinedload(Novel.author),
        joinedload(Novel.genre_links),
        joinedload(Novel.tag_links),
        joinedload(Novel.chapters),
    ).filter(Novel.status.in_([NovelStatus.PUBLISHED, NovelStatus.COMPLETED]))

    if engaged_novel_ids:
        base_query = base_query.filter(~Novel.id.in_(engaged_novel_ids))

    if genre_ids:
        base_query = base_query.join(
            NovelGenre, NovelGenre.novel_id == Novel.id
        ).filter(NovelGenre.genre_id.in_(genre_ids)).distinct()

    recommendations = (
        base_query.order_by(Novel.average_rating.desc(), Novel.views.desc())
        .limit(limit)
        .all()
    )

    if len(recommendations) < limit:
        # Top up with generally popular novels if genre-based results are thin.
        existing_ids = {n.id for n in recommendations} | engaged_novel_ids
        fallback_query = (
            db.query(Novel)
            .options(
                joinedload(Novel.author),
                joinedload(Novel.genre_links),
                joinedload(Novel.tag_links),
                joinedload(Novel.chapters),
            )
            .filter(Novel.status.in_([NovelStatus.PUBLISHED, NovelStatus.COMPLETED]))
        )
        if existing_ids:
            fallback_query = fallback_query.filter(~Novel.id.in_(existing_ids))
        fallback = (
            fallback_query.order_by(Novel.average_rating.desc(), Novel.views.desc())
            .limit(limit - len(recommendations))
            .all()
        )
        recommendations.extend(fallback)

    return recommendations
