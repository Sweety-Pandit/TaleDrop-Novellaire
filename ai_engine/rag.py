import uuid
from typing import Dict, List, TypedDict

from ai_engine import embeddings, vector_store
from ai_engine.utils import chunk_text, strip_markdown


class ChapterInput(TypedDict):
    chapter_id: str
    chapter_number: int
    chapter_title: str
    content: str


def index_novel_chapters(novel_id: uuid.UUID, chapters: List[ChapterInput]) -> int:
    vector_store.reset_novel_collection(novel_id)

    chunk_ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict] = []

    for chapter in chapters:
        plain_text = strip_markdown(chapter["content"])
        for i, chunk in enumerate(chunk_text(plain_text)):
            chunk_ids.append(f"{chapter['chapter_id']}_{i}")
            documents.append(chunk)
            metadatas.append(
                {
                    "chapter_id": chapter["chapter_id"],
                    "chapter_number": chapter["chapter_number"],
                    "chapter_title": chapter["chapter_title"],
                }
            )

    if not documents:
        return 0

    vectors = embeddings.embed_texts(documents)
    vector_store.upsert_chunks(novel_id, chunk_ids, vectors, documents, metadatas)
    return len(documents)


def retrieve_relevant_chunks(novel_id: uuid.UUID, question: str, top_k: int = 5) -> List[Dict]:
    query_vector = embeddings.embed_text(question)
    return vector_store.query_chunks(novel_id, query_vector, top_k=top_k)
