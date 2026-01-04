from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.entry_analysis import EntryAnalysis
from app.models.journal_entry import JournalEntry
from app.models.user import User
from app.schemas.report import CurrentReportOut, TrendPoint
from app.schemas.common import Language
from app.services.report_service import compute_weekly_report

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/current", response_model=CurrentReportOut)
def get_current_report(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    today = date.today()
    week_start = today - timedelta(days=6)
    week_end = today

    stmt = select(JournalEntry).where(
        JournalEntry.user_id == user.id,
        JournalEntry.created_at >= week_start,
        JournalEntry.created_at < week_end + timedelta(days=1),
    ).order_by(JournalEntry.created_at)
    entries = db.scalars(stmt).all()

    stmt_a = select(EntryAnalysis).where(
        EntryAnalysis.user_id == user.id,
        EntryAnalysis.entry_id.in_([e.id for e in entries]),
    )
    analyses = {a.entry_id: a for a in db.scalars(stmt_a).all()}

    # Build series
    series: list[TrendPoint] = []
    for e in entries:
        a = analyses.get(e.id)
        if a:
            series.append(
                TrendPoint(
                    date=e.created_at.date(),
                    geist=a.pillar_scores.get("geist", 5),
                    herz=a.pillar_scores.get("herz", 5),
                    seele=a.pillar_scores.get("seele", 5),
                    koerper=a.pillar_scores.get("koerper", 5),
                    aura=a.pillar_scores.get("aura", 5),
                )
            )

    if not analyses:
        # Fallback
        return CurrentReportOut(
            language=Language(user.preferred_language),
            week_start_date=week_start,
            week_end_date=week_end,
            pillar_scores_avg={"geist": 5, "herz": 5, "seele": 5, "koerper": 5, "aura": 5},
            pillar_trends={"geist": "flat", "herz": "flat", "seele": "flat", "koerper": "flat", "aura": "flat"},
            recurring_patterns=[],
            correlations=[],
            summary="No data available." if user.preferred_language == "en" else "Keine Daten verfügbar.",
            daily_recommendation="",
            weekly_goal="",
            series=series,
        )

    report = compute_weekly_report(db, user.id, user.preferred_language)

    return CurrentReportOut(
        language=Language(report.language),
        week_start_date=report.week_start_date,
        week_end_date=report.week_end_date,
        pillar_scores_avg=report.pillar_scores_avg,
        pillar_trends=report.pillar_trends,
        recurring_patterns=report.recurring_patterns,
        correlations=report.correlations,
        summary=report.summary,
        daily_recommendation=report.daily_recommendation,
        weekly_goal=report.weekly_goal,
        series=series,
    )


@router.post("/recompute")
def recompute_report(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    report = compute_weekly_report(db, user.id, user.preferred_language)
    return {"status": "ok", "report_id": str(report.id)}
