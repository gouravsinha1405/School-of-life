from __future__ import annotations

import logging
import re
import uuid

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm.client import get_chat
from app.llm.parsers import parse_with_repair
from app.llm.prompts import ENTRY_ANALYSIS_SYSTEM, ENTRY_ANALYSIS_USER_TEMPLATE
from app.llm.fix_prompts import (
    ENTRY_ANALYSIS_JSON_FIX_SYSTEM,
    ENTRY_ANALYSIS_PART1_JSON_FIX_SYSTEM,
    ENTRY_ANALYSIS_PART2_JSON_FIX_SYSTEM,
)
from app.core.database import SessionLocal
from app.models.entry_analysis import EntryAnalysis
from app.models.journal_entry import JournalEntry
from app.services.language_utils import detect_language, translate_lines, translate_text
from app.schemas.analysis import (
    Emotion,
    EntryAnalysisLLMOutput,
    PillarScores,
    PillarWeights,
    Recommendations,
    RiskFlags,
    Signals,
)

logger = logging.getLogger(__name__)

EMERGENCY_MESSAGE_DE = (
    "Wenn du in einer Krise bist, wende dich bitte an eine lokale Hilfsorganisation oder Notfallnummer."
)
EMERGENCY_MESSAGE_EN = (
    "If you are in crisis, please reach out to a local help organization or emergency hotline."
)


_META_PREFIX_RE = re.compile(
    r"^\s*(kurz\s*&?\s*freundlich|brief\s*&?\s*friendly|short\s*and\s*sweet|in\s*short|summary)\s*:??\s*",
    re.IGNORECASE,
)
_META_LINE_ONLY_RE = re.compile(
    r"^\s*(was\s+ich\s+wahrnehme|was\s+ich\s+sehe|beobachtung|reflection|themes|analysis)\s*:??\s*$",
    re.IGNORECASE,
)

_PART1_SKELETON = (
    '{"emotions":[],"themes":[],"pillar_weights":{"geist":0.2,"herz":0.2,"seele":0.2,'
    '"koerper":0.2,"aura":0.2},"pillar_scores":{"geist":5,"herz":5,"seele":5,'
    '"koerper":5,"aura":5},"signals":{"keywords":[],"phrases":[],"triggers":[]}}'
)

_PART2_SKELETON = (
    '{"reflection":"","recommendations":{"daily":[],"weekly":[]},"rationale_summary":"",'
    '"risk_flags":{"self_harm":false,"crisis":false,"medical":false,"violence":false}}'
)


def _strip_meta_labels(text: str) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    cleaned: list[str] = []
    for i, line in enumerate(lines):
        s = line.strip()
        # Drop standalone header-ish lines, especially near the start.
        if i < 6 and _META_LINE_ONLY_RE.match(s):
            continue
        cleaned.append(_META_PREFIX_RE.sub("", line))
    return "\n".join(cleaned).strip()


def _ensure_output_language(chat, result: EntryAnalysisLLMOutput, target_language: str) -> EntryAnalysisLLMOutput:
    # We only enforce language for user-facing strings.
    target = (target_language or "").strip().lower()
    if target not in {"de", "en"}:
        return result

    # Detect using a representative sample (reflection is the most important user-facing field).
    try:
        detected = detect_language(chat, result.reflection)
        if detected == "unknown" or detected == target:
            return result

        translated_reflection = translate_text(chat, result.reflection, target)
        translated_themes = translate_lines(chat, result.themes, target, max_items=6)

        emotion_names = [e.name for e in result.emotions]
        translated_emotion_names = translate_lines(chat, emotion_names, target, max_items=10)
        translated_emotions: list[Emotion] = []
        for idx, e in enumerate(result.emotions):
            name = translated_emotion_names[idx] if idx < len(translated_emotion_names) else e.name
            translated_emotions.append(Emotion(name=name, intensity=e.intensity))

        translated_daily = translate_lines(chat, result.recommendations.daily, target, max_items=3)
        translated_weekly = translate_lines(chat, result.recommendations.weekly, target, max_items=3)

        translated_keywords = translate_lines(chat, result.signals.keywords, target, max_items=8)
        translated_phrases = translate_lines(chat, result.signals.phrases, target, max_items=5)
        translated_triggers = translate_lines(chat, result.signals.triggers, target, max_items=5)

        translated_rationale = translate_text(chat, result.rationale_summary, target)

        return EntryAnalysisLLMOutput.model_validate(
            {
                "emotions": translated_emotions,
                "themes": translated_themes or result.themes,
                "pillar_weights": result.pillar_weights,
                "pillar_scores": result.pillar_scores,
                "reflection": translated_reflection or result.reflection,
                "recommendations": {"daily": translated_daily, "weekly": translated_weekly},
                "signals": {"keywords": translated_keywords, "phrases": translated_phrases, "triggers": translated_triggers},
                "rationale_summary": translated_rationale or result.rationale_summary,
                "risk_flags": result.risk_flags,
            }
        )
    except Exception:
        # Never let language enforcement break analysis generation.
        return result


def _default_pillar_weights() -> PillarWeights:
    return PillarWeights(geist=0.2, herz=0.2, seele=0.2, koerper=0.2, aura=0.2)


def _default_pillar_scores() -> PillarScores:
    return PillarScores(geist=5, herz=5, seele=5, koerper=5, aura=5)


def _run_micro_call(chat, prompt: str, model: type[BaseModel], *, fix_prompt: str) -> BaseModel:
    """Single micro-call with strict repair (one repair pass only)."""
    resp = chat.invoke([
        SystemMessage(content=ENTRY_ANALYSIS_SYSTEM),
        HumanMessage(content=prompt),
    ])
    raw = str(resp.content)
    # One repair attempt keeps latency low and avoids the model wandering.
    return parse_with_repair(model, raw, system_prompt=fix_prompt, max_attempts=1)


class _SignalsAndScoresOut(BaseModel):
    emotions: list[Emotion] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list, max_length=6)
    pillar_weights: PillarWeights = Field(default_factory=_default_pillar_weights)
    pillar_scores: PillarScores = Field(default_factory=_default_pillar_scores)
    signals: Signals = Field(default_factory=Signals)


class _NarrativeOut(BaseModel):
    reflection: str = Field(default="", max_length=1200)
    recommendations: Recommendations = Field(default_factory=Recommendations)
    rationale_summary: str = Field(default="", max_length=500)
    risk_flags: RiskFlags = Field(default_factory=RiskFlags)


def _get_last_entries_context(db: Session, user_id: uuid.UUID, exclude_entry_id: uuid.UUID, limit: int = 5) -> str:
    stmt = (
        select(JournalEntry)
        .where(JournalEntry.user_id == user_id, JournalEntry.id != exclude_entry_id)
        .order_by(JournalEntry.created_at.desc())
        .limit(limit)
    )
    entries = db.scalars(stmt).all()
    if not entries:
        return "No prior entries."
    lines = []
    for e in entries:
        lines.append(f"- {e.created_at.isoformat()}: mood={e.mood_score}, energy={e.energy_score}, text={e.text[:100]}...")
    return "\n".join(lines)


def _fallback_analysis(language: str) -> EntryAnalysisLLMOutput:
    return EntryAnalysisLLMOutput.model_validate(
        {
            "emotions": [],
            "themes": ["general"],
            "pillar_weights": {"geist": 0.2, "herz": 0.2, "seele": 0.2, "koerper": 0.2, "aura": 0.2},
            "pillar_scores": {"geist": 5, "herz": 5, "seele": 5, "koerper": 5, "aura": 5},
            "reflection": (
                "I couldn't generate a full analysis right now, but I'm here with you. "
                "If you can, take one slow breath in and out, and name one small thing you need today. "
                "You can also write one sentence: 'Right now I feel ___, and I need ___.'."
                if language == "en"
                else "Ich konnte gerade keine vollständige Analyse erstellen, aber ich bin da. "
                "Wenn es dir möglich ist, atme einmal langsam ein und aus und benenne eine kleine Sache, die du heute brauchst. "
                "Du kannst auch einen Satz schreiben: 'Gerade fühle ich ___, und ich brauche ___.'."
            ),
            "recommendations": {"daily": [], "weekly": []},
            "signals": {"keywords": [], "phrases": [], "triggers": []},
            "rationale_summary": "Fallback analysis.",
            "risk_flags": {"self_harm": False, "crisis": False, "medical": False, "violence": False},
        }
    )


def _inject_emergency_message(reflection: str, language: str) -> str:
    msg = EMERGENCY_MESSAGE_DE if language == "de" else EMERGENCY_MESSAGE_EN
    return f"{reflection}\n\n{msg}"


def analyze_entry(db: Session, entry: JournalEntry, user_language: str) -> EntryAnalysis:
    last_entries_context = _get_last_entries_context(db, entry.user_id, entry.id)

    user_prompt = ENTRY_ANALYSIS_USER_TEMPLATE.format(
        language=user_language,
        timestamp=entry.created_at.isoformat(),
        mood_score=entry.mood_score,
        energy_score=entry.energy_score,
        entry_text=entry.text,
        last_entries=last_entries_context,
    )

    try:
        chat = get_chat()

        # Preferred path: structured output (tool/function calling) with smaller schemas.
        # This avoids relying on the model to produce a complete JSON blob in one go.
        scores_prompt = """
User language: {language}
Timestamp: {timestamp}
Mood (1-10): {mood_score}
Energy (1-10): {energy_score}

Entry text:
{entry_text}

Optional context: last 5 entries:
{last_entries}

Task:
1) Identify emotions (name + intensity 0..1)
2) Extract up to 6 themes
3) Provide pillar_scores (1..10) and pillar_weights (0..1, sum approx 1) for: geist, herz, seele, koerper, aura
4) Provide signals (keywords, phrases, triggers)

 Soft rule for mental vs. physical strain (do not hard clamp):
 - If stress >= 6 AND energy >= 6 AND text shows mental overactivity (thinking, rumination, pressure, "can't switch off")
     AND there are no physical-fatigue signals (tired body, exhaustion, pain), then set Geist about 1 point higher than Körper.

 Natural variation: if all inputs feel balanced and within ±1, avoid perfect symmetry (e.g., 5/5/5/5/5). Introduce small ±1 differences to keep scores realistic.

Be kind, non-judgmental, and not medical. Use the user's language.
""".strip().format(
            language=user_language,
            timestamp=entry.created_at.isoformat(),
            mood_score=entry.mood_score,
            energy_score=entry.energy_score,
            entry_text=entry.text,
            last_entries=last_entries_context,
        )

        narrative_prompt = """
User language: {language}
Timestamp: {timestamp}
Mood (1-10): {mood_score}
Energy (1-10): {energy_score}

Entry text:
{entry_text}

Task:
Write a comforting, structured reflection for a German/Swiss German audience (standard German wording is fine).

Formatting (plain text):
- 1–2 short validating sentences
- 2–4 bullet points, each starting with "- "
- Then 5 short lines for pillars: "Geist: ...", "Herz: ...", "Seele: ...", "Körper: ...", "Aura: ..."
- End with 1 concrete gentle next step (one sentence)

Do NOT include meta labels or filler headings such as "Kurz & freundlich:", "Brief & friendly:", "Short and sweet:", "In short:", "Summary:", "Was ich wahrnehme:".

Also provide:
- recommendations: daily (<=3) and weekly (<=3)
- rationale_summary: max 500 chars (what signals led to scores; no chain-of-thought)
- risk_flags: self_harm, crisis, medical, violence (booleans)

 Adjust scoring nuance:
 - If stress is high, mood is low, and emotional exhaustion is present, let Herz be slightly above Körper (soft nudge, not a clamp).

 Language precision:
 - Use strictly observational language for brief explanations; avoid phrases like "shows that" or "because".
 - In reflective text, replace directives ("it is important that…") with invitational language ("it may help to…", "you might notice…").
 - Do NOT introduce clinical labels. If a trait is not explicitly named, keep it descriptive (e.g., "emotional tiredness", "self-pressure").

 Language precision:
 - Prefer descriptive phrasing over causal claims. Use "seems to show" / "may contribute to" instead of "this causes" / "this means you are".
 - Do NOT invent psychological labels unless explicitly mentioned. Replace named traits ("perfectionism", "avoidant", "attachment", "inner critic") with descriptive language like "self-pressure", "critical inner voice", "high personal expectations".

 Aura dimension framing:
 - Focus on environmental boundaries, sensory load, transition rituals, external stimulation management (e.g., reduce evening screens, quiet routines, end-of-day signals).
 - Avoid mystical/energetic claims and avoid overlapping with Geist (internal cognition).

 Preserve safety tone: non-diagnostic, no "you must/should", supportive and validating.

No diagnosis. No clinical advice. If risk is present, keep it supportive and suggest reaching out locally.
""".strip().format(
            language=user_language,
            timestamp=entry.created_at.isoformat(),
            mood_score=entry.mood_score,
            energy_score=entry.energy_score,
            entry_text=entry.text,
        )

        scores_prompt = (
            scores_prompt
            + "\n\nReturn STRICT JSON with fields: emotions, themes, pillar_weights, pillar_scores, signals."
        )
        narrative_prompt = (
            narrative_prompt
            + "\n\nReturn STRICT JSON with fields: reflection, recommendations, rationale_summary, risk_flags."
        )

        # Part 1: scores + signals
        try:
            part1 = _run_micro_call(chat, scores_prompt, _SignalsAndScoresOut, fix_prompt=ENTRY_ANALYSIS_PART1_JSON_FIX_SYSTEM)
        except Exception:
            # Retry once with an explicit JSON skeleton to keep the model concise.
            logger.warning("Analysis micro-call part1 failed, retrying with skeleton")
            narrowed = scores_prompt + "\n\nReturn EXACTLY this JSON shape (fill values, keep keys): " + _PART1_SKELETON
            try:
                part1 = _run_micro_call(chat, narrowed, _SignalsAndScoresOut, fix_prompt=ENTRY_ANALYSIS_PART1_JSON_FIX_SYSTEM)
            except Exception:
                part1 = _SignalsAndScoresOut()

        # Part 2: narrative + recommendations
        try:
            part2 = _run_micro_call(chat, narrative_prompt, _NarrativeOut, fix_prompt=ENTRY_ANALYSIS_PART2_JSON_FIX_SYSTEM)
        except Exception:
            logger.warning("Analysis micro-call part2 failed, retrying with skeleton")
            narrowed = narrative_prompt + "\n\nReturn EXACTLY this JSON shape (fill values, keep keys): " + _PART2_SKELETON
            try:
                part2 = _run_micro_call(chat, narrowed, _NarrativeOut, fix_prompt=ENTRY_ANALYSIS_PART2_JSON_FIX_SYSTEM)
            except Exception:
                part2 = _NarrativeOut()

        result = EntryAnalysisLLMOutput.model_validate(
            {
                "emotions": getattr(part1, "emotions", []),
                "themes": getattr(part1, "themes", []),
                "pillar_weights": getattr(part1, "pillar_weights", _default_pillar_weights()),
                "pillar_scores": getattr(part1, "pillar_scores", _default_pillar_scores()),
                "reflection": getattr(part2, "reflection", ""),
                "recommendations": getattr(part2, "recommendations", Recommendations()),
                "signals": getattr(part1, "signals", Signals()),
                "rationale_summary": getattr(part2, "rationale_summary", ""),
                "risk_flags": getattr(part2, "risk_flags", RiskFlags()),
            }
        )

        # Enforce that user-facing strings match the user's selected language.
        result = _ensure_output_language(chat, result, user_language)

        # Final safety-net: strip any leftover meta labels from user-facing fields.
        result.reflection = _strip_meta_labels(result.reflection)
        result.rationale_summary = _strip_meta_labels(result.rationale_summary)
        result.recommendations.daily = [_strip_meta_labels(x) for x in result.recommendations.daily]
        result.recommendations.weekly = [_strip_meta_labels(x) for x in result.recommendations.weekly]

    except Exception:
        # Fallback path: single-call + robust JSON repair.
        try:
            chat = get_chat()
            resp = chat.invoke([
                SystemMessage(content=ENTRY_ANALYSIS_SYSTEM),
                HumanMessage(content=user_prompt),
            ])
            raw = str(resp.content)
            result = parse_with_repair(EntryAnalysisLLMOutput, raw, system_prompt=ENTRY_ANALYSIS_JSON_FIX_SYSTEM)
            result = _ensure_output_language(chat, result, user_language)
            result.reflection = _strip_meta_labels(result.reflection)
            result.rationale_summary = _strip_meta_labels(result.rationale_summary)
            result.recommendations.daily = [_strip_meta_labels(x) for x in result.recommendations.daily]
            result.recommendations.weekly = [_strip_meta_labels(x) for x in result.recommendations.weekly]
        except Exception:
            logger.exception("LLM analysis failed for entry %s", entry.id)
            result = _fallback_analysis(user_language)

    # Safety: if risk flags present, inject emergency message
    if result.risk_flags.self_harm or result.risk_flags.crisis:
        result.reflection = _inject_emergency_message(result.reflection, user_language)
        result.recommendations.daily = []
        result.recommendations.weekly = []

    existing = db.scalars(select(EntryAnalysis).where(EntryAnalysis.entry_id == entry.id)).first()
    if existing:
        existing.language = user_language
        existing.emotions = [e.model_dump() for e in result.emotions]
        existing.themes = result.themes
        existing.pillar_weights = result.pillar_weights.model_dump()
        existing.pillar_scores = result.pillar_scores.model_dump()
        existing.reflection = result.reflection
        existing.recommendations = result.recommendations.model_dump()
        existing.signals = result.signals.model_dump()
        existing.rationale_summary = result.rationale_summary
        existing.risk_flags = result.risk_flags.model_dump()
        db.commit()
        db.refresh(existing)
        return existing

    analysis = EntryAnalysis(
        id=uuid.uuid4(),
        entry_id=entry.id,
        user_id=entry.user_id,
        language=user_language,
        emotions=[e.model_dump() for e in result.emotions],
        themes=result.themes,
        pillar_weights=result.pillar_weights.model_dump(),
        pillar_scores=result.pillar_scores.model_dump(),
        reflection=result.reflection,
        recommendations=result.recommendations.model_dump(),
        signals=result.signals.model_dump(),
        rationale_summary=result.rationale_summary,
        risk_flags=result.risk_flags.model_dump(),
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def analyze_entry_background(entry_id: str, user_language: str) -> None:
    try:
        entry_uuid = uuid.UUID(entry_id)
    except ValueError:
        logger.error("Invalid entry_id for background analysis: %s", entry_id)
        return

    db = SessionLocal()
    try:
        entry = db.get(JournalEntry, entry_uuid)
        if not entry:
            logger.error("Entry not found for background analysis: %s", entry_id)
            return
        analyze_entry(db, entry, user_language)
    finally:
        db.close()
