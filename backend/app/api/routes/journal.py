from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.journal_entry import JournalEntry
from app.models.user import User
from app.schemas.analysis import EntryAnalysisOut
from app.schemas.journal import JournalEntryCreate, JournalEntryCreatedResponse, JournalEntryOut
from app.services.analysis_service import analyze_entry

router = APIRouter(prefix="/api/journal", tags=["journal"])


@router.post("", response_model=JournalEntryCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_entry(
    data: JournalEntryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = JournalEntry(
        id=uuid.uuid4(),
        user_id=user.id,
        text=data.text,
        mood_score=data.mood_score,
        energy_score=data.energy_score,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Run analysis synchronously so the user sees results immediately after saving.
    analyze_entry(db, entry, user.preferred_language)

    return JournalEntryCreatedResponse(
        entry=JournalEntryOut(
            id=str(entry.id),
            text=entry.text,
            mood_score=entry.mood_score,
            energy_score=entry.energy_score,
            created_at=entry.created_at,
        ),
        analysis_status="ready",
    )


@router.get("", response_model=list[JournalEntryOut])
def list_entries(
    limit: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(JournalEntry).where(JournalEntry.user_id == user.id).order_by(JournalEntry.created_at.desc()).limit(limit)
    entries = db.scalars(stmt).all()
    return [
        JournalEntryOut(
            id=str(e.id),
            text=e.text,
            mood_score=e.mood_score,
            energy_score=e.energy_score,
            created_at=e.created_at,
        )
        for e in entries
    ]


@router.get("/{entry_id}", response_model=JournalEntryOut)
def get_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        entry_uuid = uuid.UUID(entry_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    entry = db.get(JournalEntry, entry_uuid)
    if not entry or entry.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")
    return JournalEntryOut(
        id=str(entry.id),
        text=entry.text,
        mood_score=entry.mood_score,
        energy_score=entry.energy_score,
        created_at=entry.created_at,
    )


@router.get("/{entry_id}/analysis", response_model=EntryAnalysisOut | None)
def get_entry_analysis(
    entry_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        entry_uuid = uuid.UUID(entry_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    entry = db.get(JournalEntry, entry_uuid)
    if not entry or entry.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    if not entry.analysis:
        return None

    a = entry.analysis
    return EntryAnalysisOut(
        id=str(a.id),
        entry_id=str(a.entry_id),
        user_id=str(a.user_id),
        language=a.language,
        emotions=a.emotions,
        themes=a.themes,
        pillar_weights=a.pillar_weights,
        pillar_scores=a.pillar_scores,
        reflection=a.reflection,
        recommendations=a.recommendations,
        signals=a.signals,
        rationale_summary=a.rationale_summary,
        risk_flags=a.risk_flags,
    )


@router.post("/{entry_id}/analysis/recompute", response_model=EntryAnalysisOut)
def recompute_entry_analysis(
    entry_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        entry_uuid = uuid.UUID(entry_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    entry = db.get(JournalEntry, entry_uuid)
    if not entry or entry.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entry not found")

    a = analyze_entry(db, entry, user.preferred_language)
    return EntryAnalysisOut(
        id=str(a.id),
        entry_id=str(a.entry_id),
        user_id=str(a.user_id),
        language=a.language,
        emotions=a.emotions,
        themes=a.themes,
        pillar_weights=a.pillar_weights,
        pillar_scores=a.pillar_scores,
        reflection=a.reflection,
        recommendations=a.recommendations,
        signals=a.signals,
        rationale_summary=a.rationale_summary,
        risk_flags=a.risk_flags,
    )
