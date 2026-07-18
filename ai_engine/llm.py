import os
from typing import Optional

import ollama

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

_client: Optional[ollama.Client] = None


def get_ollama_client() -> ollama.Client:
    """Lazily create and cache a single Ollama client pointed at the local server."""
    global _client
    if _client is None:
        _client = ollama.Client(host=OLLAMA_BASE_URL)
    return _client


def generate(prompt: str, system: Optional[str] = None, temperature: float = 0.3) -> str:
    """
    Generate a single text completion from the local Ollama model.

    """
    client = get_ollama_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={"temperature": temperature},
        )
    except Exception as exc: 
        raise RuntimeError(
            f"Unable to reach Ollama at {OLLAMA_BASE_URL} with model '{OLLAMA_MODEL}': {exc}"
        ) from exc

    return response["message"]["content"].strip()
