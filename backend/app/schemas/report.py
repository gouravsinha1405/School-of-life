from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from app.schemas.common import Language


class WeeklyReportLLMOutput(BaseModel):
    pillar_scores_avg: dict
    pillar_trends: dict
    recurring_patterns: list = Field(default_factory=list)
    correlations: list = Field(default_factory=list)
    summary: str = Field(max_length=2000)
    daily_recommendation: str = Field(max_length=800)
    weekly_goal: str = Field(max_length=800)


class TrendPoint(BaseModel):
    date: date
    geist: int
    herz: int
    seele: int
    koerper: int
    aura: int


class CurrentReportOut(BaseModel):
    language: Language
    week_start_date: date
    week_end_date: date
    pillar_scores_avg: dict
    pillar_trends: dict
    recurring_patterns: list
    correlations: list
    summary: str
    daily_recommendation: str
    weekly_goal: str
    series: list[TrendPoint]
