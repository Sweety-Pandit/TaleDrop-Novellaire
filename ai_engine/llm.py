import os
from typing import Optional
import httpx
import ollama
AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama").strip().lower()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

_client: Optional[ollama.Client] = None


def get_ollama_client() -> ollama.Client:
    """Lazily create and cache a single Ollama client pointed at the local server."""
    global _client
    if _client is None:
        _client = ollama.Client(host=OLLAMA_BASE_URL)
    return _client


def _generate_ollama(prompt: str, system: Optional[str] = None, temperature: float = 0.3) -> str:
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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _generate_gemini(prompt: str, system: Optional[str], temperature: float) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "AI_PROVIDER is set to 'gemini' but GEMINI_API_KEY is not set"
        )

    url = f"{GEMINI_API_BASE}/{GEMINI_MODEL}:generateContent"
    body: dict = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature},
    }
    if system:
        body["system_instruction"] = {"parts": [{"text": system}]}

    try:
        response = httpx.post(
            url,
            headers={"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"},
            json=body,
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as exc:  # noqa: BLE001 - surface any Gemini/connection failure uniformly
        raise RuntimeError(
            f"Unable to reach the Gemini API with model '{GEMINI_MODEL}': {exc}"
        ) from exc


# --- Public entry point ---------------------------------------------------
def generate(prompt: str, system: Optional[str] = None, temperature: float = 0.3) -> str:
    """
    Generate a single text completion from the configured AI provider (Ollama or Gemini).
    """
    if AI_PROVIDER == "gemini":
        return _generate_gemini(prompt, system, temperature)
    return _generate_ollama(prompt, system, temperature)