from __future__ import annotations

import json
import re
from typing import TypeVar

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ValidationError

from app.llm.client import get_chat
from app.llm.prompts import JSON_FIX_SYSTEM

T = TypeVar("T", bound=BaseModel)


_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def extract_json_object(text: str) -> str:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    m = _JSON_RE.search(text)
    if not m:
        raise ValueError("No JSON object found")
    return m.group(0)


def parse_and_validate(model: type[T], raw_text: str) -> T:
    json_text = extract_json_object(raw_text)
    data = json.loads(json_text)
    return model.model_validate(data)


def repair_json(raw_text: str, *, system_prompt: str = JSON_FIX_SYSTEM) -> str:
    chat = get_chat()
    resp = chat.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=raw_text),
    ])
    return str(resp.content)


def parse_with_repair(
    model: type[T],
    raw_text: str,
    *,
    max_attempts: int = 2,
    system_prompt: str = JSON_FIX_SYSTEM,
) -> T:
    last_err: Exception | None = None
    text = raw_text
    for _ in range(max_attempts + 1):
        try:
            return parse_and_validate(model, text)
        except (json.JSONDecodeError, ValueError, ValidationError) as e:
            last_err = e
            text = repair_json(text, system_prompt=system_prompt)
    raise last_err or ValueError("Failed to parse JSON")
