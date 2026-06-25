"""Gemini embeddings + chat. The only module that talks to the LLM provider."""
from __future__ import annotations

import google.generativeai as genai

from app.config import settings

_configured = False


class ProviderNotConfigured(RuntimeError):
    """Raised when the LLM provider (Gemini) has no API key configured."""


def _ensure_configured() -> None:
    global _configured
    if not _configured:
        if not settings.gemini_api_key:
            raise ProviderNotConfigured(
                "GEMINI_API_KEY is not set. Add it to your .env to enable "
                "embeddings, search, and chat."
            )
        genai.configure(api_key=settings.gemini_api_key)
        _configured = True


def embed_texts(texts: list[str], task_type: str = "retrieval_document") -> list[list[float]]:
    _ensure_configured()
    vectors: list[list[float]] = []
    for text in texts:
        result = genai.embed_content(
            model=settings.embedding_model,
            content=text,
            task_type=task_type,
        )
        vectors.append(result["embedding"])
    return vectors


def embed_query(text: str) -> list[float]:
    return embed_texts([text], task_type="retrieval_query")[0]


def generate(prompt: str) -> str:
    _ensure_configured()
    model = genai.GenerativeModel(settings.chat_model)
    response = model.generate_content(prompt)
    return (response.text or "").strip()
