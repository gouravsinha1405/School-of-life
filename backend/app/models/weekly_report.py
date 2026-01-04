from __future__ import annotations

from datetime import date, datetime
import uuid

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    week_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    language: Mapped[str] = mapped_column(String(2), nullable=False)

    pillar_scores_avg: Mapped[dict] = mapped_column(JSONB, nullable=False)
    pillar_trends: Mapped[dict] = mapped_column(JSONB, nullable=False)
    recurring_patterns: Mapped[list] = mapped_column(JSONB, nullable=False)
    correlations: Mapped[list] = mapped_column(JSONB, nullable=False)

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    daily_recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    weekly_goal: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="weekly_reports")
