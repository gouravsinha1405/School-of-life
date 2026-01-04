from __future__ import annotations

import json
from typing import TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, ValidationError

from app.llm.parsers import extract_json_object
from app.schemas.common import Language

T = TypeVar("T", bound=BaseModel)


_LANGUAGE_DETECT_SYSTEM = """
You are a language detector.

Given the provided text, output ONLY a JSON object matching this schema:
{"language": "de"|"en"}

Rules:
- Return ONLY valid JSON. No markdown. No code fences. No extra keys.
- Choose the dominant language of the text.
""".strip()

_LANGUAGE_DETECT_JSON_FIX_SYSTEM = """
You are a strict JSON repair tool.
Return ONLY a valid JSON object with exactly this schema:
{"language": "de"|"en"}
No markdown. No explanation.
""".strip()

_TRANSLATE_TEXT_SYSTEM = """
You are a translator.

Translate the provided text into the target language.
Output ONLY a JSON object matching this schema:
{"text": string}

Rules:
- Return ONLY valid JSON. No markdown. No code fences. No extra keys.
- Preserve meaning; keep tone kind and non-judgmental.
""".strip()

_TRANSLATE_TEXT_JSON_FIX_SYSTEM = """
You are a strict JSON repair tool.
Return ONLY a valid JSON object with exactly this schema:
{"text": string}
No markdown. No explanation.
""".strip()

_TRANSLATE_LINES_SYSTEM = """
You are a translator.

Translate each line into the target language.
Output ONLY a JSON object matching this schema:
{"lines": [string, ...]}

Rules:
- Return ONLY valid JSON. No markdown. No code fences. No extra keys.
- Keep the same number of lines and the same order.
""".strip()

_TRANSLATE_LINES_JSON_FIX_SYSTEM = """
You are a strict JSON repair tool.
Return ONLY a valid JSON object with exactly this schema:
{"lines": [string, ...]}
No markdown. No explanation.
""".strip()


class _DetectedLanguageOut(BaseModel):
    language: Language


class _TranslatedTextOut(BaseModel):
    text: str = Field(default="")


class _TranslatedLinesOut(BaseModel):
    lines: list[str] = Field(default_factory=list)


def _repair_json_with_chat(chat, raw_text: str, system_prompt: str) -> str:
    resp = chat.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=raw_text),
        ]
    )
    return str(resp.content)


def _parse_and_validate(model: type[T], raw_text: str) -> T:
    json_text = extract_json_object(raw_text)
    data = json.loads(json_text)
    return model.model_validate(data)


def _parse_with_repair_using_chat(
    chat,
    model: type[T],
    raw_text: str,
    *,
    max_attempts: int = 1,
    repair_system_prompt: str,
) -> T:
    last_err: Exception | None = None
    text = raw_text
    for _ in range(max_attempts + 1):
        try:
            return _parse_and_validate(model, text)
        except (json.JSONDecodeError, ValueError, ValidationError) as e:
            last_err = e
            text = _repair_json_with_chat(chat, text, repair_system_prompt)
    raise last_err or ValueError("Failed to parse JSON")


def detect_language(chat, text: str) -> str:
    s = (text or "").strip()
    if not s:
        return "unknown"

    try:
        resp = chat.invoke(
            [
                SystemMessage(content=_LANGUAGE_DETECT_SYSTEM),
                HumanMessage(content=s),
            ]
        )
        raw = str(resp.content)
        out = _parse_with_repair_using_chat(
            chat,
            _DetectedLanguageOut,
            raw,
            max_attempts=1,
            repair_system_prompt=_LANGUAGE_DETECT_JSON_FIX_SYSTEM,
        )
        return out.language.value
    except Exception:
        return "unknown"


def translate_text(chat, text: str, target_language: str) -> str:
    s = (text or "").strip()
    target = (target_language or "").strip().lower()
    if not s:
        return ""
    if target not in {"de", "en"}:
        return s

    try:
        resp = chat.invoke(
            [
                SystemMessage(content=_TRANSLATE_TEXT_SYSTEM),
                HumanMessage(content=f"Target language: {target}\n\nText:\n{s}"),
            ]
        )
        raw = str(resp.content)
        out = _parse_with_repair_using_chat(
            chat,
            _TranslatedTextOut,
            raw,
            max_attempts=1,
            repair_system_prompt=_TRANSLATE_TEXT_JSON_FIX_SYSTEM,
        )
        return (out.text or "").strip()
    except Exception:
        return s


def translate_lines(chat, items: list[str], target_language: str, *, max_items: int) -> list[str]:
    target = (target_language or "").strip().lower()
    cleaned = [i.strip() for i in (items or []) if i and i.strip()]
    cleaned = cleaned[:max_items]
    if not cleaned:
        return []
    if target not in {"de", "en"}:
        return cleaned

    try:
        payload = json.dumps({"lines": cleaned}, ensure_ascii=False)
        resp = chat.invoke(
            [
                SystemMessage(content=_TRANSLATE_LINES_SYSTEM),
                HumanMessage(content=f"Target language: {target}\n\nInput JSON:\n{payload}"),
            ]
        )
        raw = str(resp.content)
        out = _parse_with_repair_using_chat(
            chat,
            _TranslatedLinesOut,
            raw,
            max_attempts=1,
            repair_system_prompt=_TRANSLATE_LINES_JSON_FIX_SYSTEM,
        )
        out_lines = [ln.strip() for ln in (out.lines or []) if ln and ln.strip()]
        if len(out_lines) != len(cleaned):
            return cleaned
        return out_lines[: len(cleaned)]
    except Exception:
        return cleaned
