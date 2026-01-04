from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class JournalEntryCreate(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    mood_score: int = Field(ge=1, le=10)
    energy_score: int = Field(ge=1, le=10)


class JournalEntryOut(BaseModel):
    id: str
    text: str
    mood_score: int
    energy_score: int
    created_at: datetime


class JournalEntryCreatedResponse(BaseModel):
    entry: JournalEntryOut
    analysis_status: str
