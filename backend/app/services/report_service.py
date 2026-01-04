from __future__ import annotations

import logging
import uuid
from datetime import date, timedelta

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.llm.client import get_chat
from app.llm.parsers import parse_with_repair
from app.llm.prompts import WEEKLY_REPORT_SYSTEM, WEEKLY_REPORT_USER_TEMPLATE
from app.llm.fix_prompts import WEEKLY_REPORT_JSON_FIX_SYSTEM
from app.models.entry_analysis import EntryAnalysis
from app.models.journal_entry import JournalEntry
from app.models.weekly_report import WeeklyReport
from app.schemas.report import WeeklyReportLLMOutput
from app.services.language_utils import detect_language, translate_text

logger = logging.getLogger(__name__)


def _ensure_weekly_report_language(chat, result: WeeklyReportLLMOutput, target_language: str) -> WeeklyReportLLMOutput:
    target = (target_language or "").strip().lower()
    if target not in {"de", "en"}:
        return result
    detected = detect_language(chat, result.summary)
    if detected == "unknown" or detected == target:
        return result

    try:
        return WeeklyReportLLMOutput.model_validate(
            {
                **result.model_dump(),
                "summary": translate_text(chat, result.summary, target) or result.summary,
                "daily_recommendation": translate_text(chat, result.daily_recommendation, target)
                or result.daily_recommendation,
                "weekly_goal": translate_text(chat, result.weekly_goal, target) or result.weekly_goal,
            }
        )
    except Exception:
        return result


def _fallback_report(language: str, week_start: date, week_end: date) -> WeeklyReportLLMOutput:
    return WeeklyReportLLMOutput(
        pillar_scores_avg={"geist": 5, "herz": 5, "seele": 5, "koerper": 5, "aura": 5},
        pillar_trends={"geist": "flat", "herz": "flat", "seele": "flat", "koerper": "flat", "aura": "flat"},
        recurring_patterns=[],
        correlations=[],
        summary="No data available for this week." if language == "en" else "Keine Daten für diese Woche verfügbar.",
        daily_recommendation="",
        weekly_goal="",
    )


def compute_weekly_report(db: Session, user_id, user_language: str) -> WeeklyReport:
    today = date.today()
    week_start = today - timedelta(days=6)
    week_end = today

    stmt = select(JournalEntry).where(
        JournalEntry.user_id == user_id,
        JournalEntry.created_at >= week_start,
        JournalEntry.created_at < week_end + timedelta(days=1),
    ).order_by(JournalEntry.created_at)
    entries = db.scalars(stmt).all()

    stmt_a = select(EntryAnalysis).where(
        EntryAnalysis.user_id == user_id,
        EntryAnalysis.entry_id.in_([e.id for e in entries]),
    )
    analyses = db.scalars(stmt_a).all()

    entry_stats = [
        {
            "id": e.id,
            "created_at": e.created_at.isoformat(),
            "mood": e.mood_score,
            "energy": e.energy_score,
        }
        for e in entries
    ]

    analyses_dump = [
        {
            "entry_id": a.entry_id,
            "pillar_scores": a.pillar_scores,
            "themes": a.themes,
        }
        for a in analyses
    ]

    user_prompt = WEEKLY_REPORT_USER_TEMPLATE.format(
        language=user_language,
        week_start_date=week_start.isoformat(),
        week_end_date=week_end.isoformat(),
        entry_stats=entry_stats,
        analyses=analyses_dump,
    )

    try:
        chat = get_chat()
        resp = chat.invoke([
            SystemMessage(content=WEEKLY_REPORT_SYSTEM),
            HumanMessage(content=user_prompt),
        ])
        raw = str(resp.content)
        result = parse_with_repair(WeeklyReportLLMOutput, raw, system_prompt=WEEKLY_REPORT_JSON_FIX_SYSTEM)
        result = _ensure_weekly_report_language(chat, result, user_language)
    except Exception as e:
        logger.exception("Weekly report LLM failed for user %s", user_id)
        result = _fallback_report(user_language, week_start, week_end)

    report = WeeklyReport(
        id=uuid.uuid4(),
        user_id=user_id,
        week_start_date=week_start,
        week_end_date=week_end,
        language=user_language,
        pillar_scores_avg=result.pillar_scores_avg,
        pillar_trends=result.pillar_trends,
        recurring_patterns=result.recurring_patterns,
        correlations=result.correlations,
        summary=result.summary,
        daily_recommendation=result.daily_recommendation,
        weekly_goal=result.weekly_goal,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
