"""
ai_engine

Local AI functionality for TaleDrop-Novellaire: story summaries,
RAG-based question answering over a novel's chapters, and the
retrieval/embedding/vector-store plumbing that supports them.

Runs entirely locally: Ollama for generation, Sentence Transformers
for embeddings, ChromaDB for the vector store. No external AI API
calls are made.
"""
