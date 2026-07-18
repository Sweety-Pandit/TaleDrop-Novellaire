import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models import Chapter, ChapterStatus, Novel, NovelStatus, Payment, PaymentStatus, User, UserRole
from app.schemas import ChapterCreate, ChapterUpdate

_CHAPTER_LOAD_OPTIONS = (joinedload(Chapter.novel),)

# Internal helpers
def _is_owner_or_admin(novel: Novel, user: Optional[User]) -> bool:
    return user is not None and (user.id == novel.author_id or user.role == UserRole.ADMIN)


def _assert_novel_ownership(novel: Novel, user: User) -> None:
    if not _is_owner_or_admin(novel, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify chapters on this novel",
        )


def user_has_purchased_chapter(db: Session, user: User, chapter: Chapter) -> bool:
    """True if the user has a successful payment for this chapter or its whole novel."""
    return (
        db.query(Payment)
        .filter(
            Payment.user_id == user.id,
            Payment.status == PaymentStatus.SUCCESS,
            (Payment.chapter_id == chapter.id) | (Payment.novel_id == chapter.novel_id),
        )
        .first()
        is not None
    )


def _next_chapter_number(db: Session, novel_id: uuid.UUID) -> int:
    max_number = (
        db.query(Chapter.chapter_number)
        .filter(Chapter.novel_id == novel_id)
        .order_by(Chapter.chapter_number.desc())
        .first()
    )
    return (max_number[0] + 1) if max_number else 1


def _assert_chapter_number_available(
    db: Session,
    novel_id: uuid.UUID,
    chapter_number: int,
    exclude_chapter_id: Optional[uuid.UUID] = None,
) -> None:
    query = db.query(Chapter).filter(
        Chapter.novel_id == novel_id, Chapter.chapter_number == chapter_number
    )
    if exclude_chapter_id is not None:
        query = query.filter(Chapter.id != exclude_chapter_id)
    if query.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chapter number {chapter_number} already exists for this novel",
        )

# Fetching
def get_chapter_by_id(db: Session, chapter_id: uuid.UUID) -> Chapter:
    """Plain fetch by id (for management routes). 404 if missing."""
    chapter = (
        db.query(Chapter)
        .options(*_CHAPTER_LOAD_OPTIONS)
        .filter(Chapter.id == chapter_id)
        .first()
    )
    if chapter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return chapter


def list_chapters_for_novel(db: Session, novel: Novel, viewer: Optional[User]) -> List[Chapter]:

    can_see_all = _is_owner_or_admin(novel, viewer)

    query = db.query(Chapter).filter(Chapter.novel_id == novel.id)
    if not can_see_all:
        query = query.filter(Chapter.status == ChapterStatus.PUBLISHED)

    return query.order_by(Chapter.chapter_number.asc()).all()


def get_chapter_for_viewer(
    db: Session, novel: Novel, chapter_number: int, viewer: Optional[User]
) -> Chapter:
    chapter = (
        db.query(Chapter)
        .options(*_CHAPTER_LOAD_OPTIONS)
        .filter(Chapter.novel_id == novel.id, Chapter.chapter_number == chapter_number)
        .first()
    )
    if chapter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    can_manage = _is_owner_or_admin(novel, viewer)
    if chapter.status == ChapterStatus.DRAFT and not can_manage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    chapter.views += 1
    db.commit()
    db.refresh(chapter)
    return chapter


def is_chapter_locked(db: Session, novel: Novel, chapter: Chapter, viewer: Optional[User]) -> bool:
    """True if the viewer is not allowed to read this chapter (premium and not purchased)."""
    if not chapter.is_premium:
        return False
    if _is_owner_or_admin(novel, viewer):
        return False
    if viewer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in to access this premium chapter",
        )
    return not user_has_purchased_chapter(db, viewer, chapter)


# Mutations
def create_chapter(
    db: Session, novel: Novel, current_user: User, payload: ChapterCreate
) -> Chapter:
    _assert_novel_ownership(novel, current_user)

    if payload.chapter_number is not None:
        _assert_chapter_number_available(db, novel.id, payload.chapter_number)
        chapter_number = payload.chapter_number
    else:
        chapter_number = _next_chapter_number(db, novel.id)

    chapter = Chapter(
        novel_id=novel.id,
        chapter_number=chapter_number,
        title=payload.title,
        content=payload.content,
        is_premium=payload.is_premium,
        price=payload.price,
        status=ChapterStatus.DRAFT,
    )
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


def update_chapter(
    db: Session, chapter: Chapter, novel: Novel, current_user: User, payload: ChapterUpdate
) -> Chapter:
    _assert_novel_ownership(novel, current_user)

    update_data = payload.model_dump(exclude_unset=True)

    if "chapter_number" in update_data:
        new_number = update_data["chapter_number"]
        if new_number != chapter.chapter_number:
            _assert_chapter_number_available(
                db, chapter.novel_id, new_number, exclude_chapter_id=chapter.id
            )

    for field, value in update_data.items():
        setattr(chapter, field, value)

    db.commit()
    db.refresh(chapter)
    return chapter


def delete_chapter(db: Session, chapter: Chapter, novel: Novel, current_user: User) -> None:
    _assert_novel_ownership(novel, current_user)
    db.delete(chapter)
    db.commit()


def set_chapter_status(
    db: Session, chapter: Chapter, novel: Novel, current_user: User, new_status: ChapterStatus
) -> Chapter:
    _assert_novel_ownership(novel, current_user)
    chapter.status = new_status
    db.commit()
    db.refresh(chapter)
    return chapter
