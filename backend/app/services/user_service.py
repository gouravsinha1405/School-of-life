from __future__ import annotations

import json
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entry_analysis import EntryAnalysis
from app.models.journal_entry import JournalEntry
from app.models.user import User
from app.models.weekly_report import WeeklyReport


def export_user_data(db: Session, user_id) -> dict:
    user = db.get(User, user_id)
    if not user:
        raise ValueError("User not found")

    entries = db.scalars(select(JournalEntry).where(JournalEntry.user_id == user_id)).all()
    analyses = db.scalars(select(EntryAnalysis).where(EntryAnalysis.user_id == user_id)).all()
    reports = db.scalars(select(WeeklyReport).where(WeeklyReport.user_id == user_id)).all()

    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "preferred_language": user.preferred_language,
            "created_at": user.created_at.isoformat(),
        },
        "journal_entries": [
            {
                "id": str(e.id),
                "text": e.text,
                "mood_score": e.mood_score,
                "energy_score": e.energy_score,
                "created_at": e.created_at.isoformat(),
            }
            for e in entries
        ],
        "analyses": [
            {
                "id": str(a.id),
                "entry_id": str(a.entry_id),
                "language": a.language,
                "emotions": a.emotions,
                "themes": a.themes,
                "pillar_weights": a.pillar_weights,
                "pillar_scores": a.pillar_scores,
                "reflection": a.reflection,
                "recommendations": a.recommendations,
                "signals": a.signals,
                "rationale_summary": a.rationale_summary,
                "risk_flags": a.risk_flags,
                "created_at": a.created_at.isoformat(),
            }
            for a in analyses
        ],
        "weekly_reports": [
            {
                "id": str(r.id),
                "week_start_date": r.week_start_date.isoformat(),
                "week_end_date": r.week_end_date.isoformat(),
                "language": r.language,
                "pillar_scores_avg": r.pillar_scores_avg,
                "pillar_trends": r.pillar_trends,
                "recurring_patterns": r.recurring_patterns,
                "correlations": r.correlations,
                "summary": r.summary,
                "daily_recommendation": r.daily_recommendation,
                "weekly_goal": r.weekly_goal,
                "created_at": r.created_at.isoformat(),
            }
            for r in reports
        ],
    }


def delete_user_account(db: Session, user_id) -> None:
    user = db.get(User, user_id)
    if not user:
        raise ValueError("User not found")
    db.delete(user)
    db.commit()
