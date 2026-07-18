import os
import uuid
from typing import Dict, List

import chromadb

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

_client = None


def get_chroma_client():
    """Lazily create and cache a single persistent ChromaDB client."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return _client


def _collection_name(novel_id: uuid.UUID) -> str:
    return f"novel_{str(novel_id).replace('-', '')}"


def get_novel_collection(novel_id: uuid.UUID):
    """Get or create the ChromaDB collection for a given novel's chapter chunks."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=_collection_name(novel_id), embedding_function=None
    )


def reset_novel_collection(novel_id: uuid.UUID) -> None:
    """Delete and recreate a novel's collection, used before a full re-index."""
    client = get_chroma_client()
    try:
        client.delete_collection(name=_collection_name(novel_id))
    except Exception:  # noqa: BLE001 - collection may not exist yet, that's fine
        pass


def upsert_chunks(
    novel_id: uuid.UUID,
    chunk_ids: List[str],
    embeddings: List[List[float]],
    documents: List[str],
    metadatas: List[Dict],
) -> None:
    """Add or update chunk vectors in a novel's collection."""
    if not chunk_ids:
        return
    collection = get_novel_collection(novel_id)
    collection.upsert(
        ids=chunk_ids, embeddings=embeddings, documents=documents, metadatas=metadatas
    )


def query_chunks(
    novel_id: uuid.UUID, query_embedding: List[float], top_k: int = 5
) -> List[Dict]:
    collection = get_novel_collection(novel_id)
    if collection.count() == 0:
        return []

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    return [
        {"document": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]
