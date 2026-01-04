from __future__ import annotations

from langchain_groq import ChatGroq

from app.core.config import settings


def get_chat() -> ChatGroq:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model_name,
        temperature=0.2,
        max_tokens=1200,
    )
