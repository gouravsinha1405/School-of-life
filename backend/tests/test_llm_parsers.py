import json

import pytest

from app.llm.parsers import extract_json_object, parse_and_validate
from app.schemas.analysis import EntryAnalysisLLMOutput


def test_extract_json_object_simple():
    text = '{"emotions": [], "themes": []}'
    result = extract_json_object(text)
    assert result == '{"emotions": [], "themes": []}'


def test_extract_json_object_with_markdown():
    text = '```json\n{"emotions": []}\n```'
    result = extract_json_object(text)
    assert '{"emotions": []}' in result


def test_parse_and_validate_valid():
    raw = json.dumps({
        "emotions": [{"name": "happy", "intensity": 0.8}],
        "themes": ["joy"],
        "pillar_weights": {"geist": 0.2, "herz": 0.2, "seele": 0.2, "koerper": 0.2, "aura": 0.2},
        "pillar_scores": {"geist": 7, "herz": 8, "seele": 6, "koerper": 5, "aura": 7},
        "reflection": "You seem happy.",
        "recommendations": {"daily": ["meditate"], "weekly": ["exercise"]},
        "signals": {"keywords": ["happy"], "phrases": [], "triggers": []},
        "rationale_summary": "High mood.",
        "risk_flags": {"self_harm": False, "crisis": False, "medical": False, "violence": False},
    })
    result = parse_and_validate(EntryAnalysisLLMOutput, raw)
    assert result.themes == ["joy"]
    assert result.emotions[0].name == "happy"


def test_parse_and_validate_invalid_json():
    raw = "not json"
    with pytest.raises((json.JSONDecodeError, ValueError)):
        parse_and_validate(EntryAnalysisLLMOutput, raw)
