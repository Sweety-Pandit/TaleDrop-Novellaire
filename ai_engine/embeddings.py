import os
from typing import List, Optional

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

_model = None


def get_embedding_model():
    """Lazily load and cache the SentenceTransformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of texts, returning one dense vector per input string."""
    if not texts:
        return []
    model = get_embedding_model()
    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return [vector.tolist() for vector in vectors]


def embed_text(text: str) -> List[float]:
    """Embed a single piece of text (e.g. a reader's question)."""
    return embed_texts([text])[0]
