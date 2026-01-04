from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base


class EntryAnalysis(Base):
    __tablename__ = "entry_analysis"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)

    entry_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("journal_entries.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    language: Mapped[str] = mapped_column(String(2), nullable=False)

    emotions: Mapped[list] = mapped_column(JSONB, nullable=False)
    themes: Mapped[list] = mapped_column(JSONB, nullable=False)
    pillar_weights: Mapped[dict] = mapped_column(JSONB, nullable=False)
    pillar_scores: Mapped[dict] = mapped_column(JSONB, nullable=False)

    reflection: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[dict] = mapped_column(JSONB, nullable=False)

    signals: Mapped[dict] = mapped_column(JSONB, nullable=False)
    rationale_summary: Mapped[str] = mapped_column(Text, nullable=False)
    risk_flags: Mapped[dict] = mapped_column(JSONB, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="entry_analyses")
    entry = relationship("JournalEntry", back_populates="analysis")
