from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import Language, PILLARS


class Emotion(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    intensity: float = Field(ge=0.0, le=1.0)


class PillarWeights(BaseModel):
    geist: float = Field(ge=0.0, le=1.0)
    herz: float = Field(ge=0.0, le=1.0)
    seele: float = Field(ge=0.0, le=1.0)
    koerper: float = Field(ge=0.0, le=1.0)
    aura: float = Field(ge=0.0, le=1.0)


class PillarScores(BaseModel):
    geist: int = Field(ge=1, le=10)
    herz: int = Field(ge=1, le=10)
    seele: int = Field(ge=1, le=10)
    koerper: int = Field(ge=1, le=10)
    aura: int = Field(ge=1, le=10)


class Recommendations(BaseModel):
    daily: list[str] = Field(default_factory=list, max_length=3)
    weekly: list[str] = Field(default_factory=list, max_length=3)


class Signals(BaseModel):
    keywords: list[str] = Field(default_factory=list, max_length=8)
    phrases: list[str] = Field(default_factory=list, max_length=5)
    triggers: list[str] = Field(default_factory=list, max_length=5)


class RiskFlags(BaseModel):
    self_harm: bool = False
    crisis: bool = False
    medical: bool = False
    violence: bool = False


class EntryAnalysisLLMOutput(BaseModel):
    emotions: list[Emotion] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list, max_length=6)
    pillar_weights: PillarWeights
    pillar_scores: PillarScores
    reflection: str = Field(max_length=1200)
    recommendations: Recommendations = Field(default_factory=Recommendations)
    signals: Signals = Field(default_factory=Signals)
    rationale_summary: str = Field(default="", max_length=500)
    risk_flags: RiskFlags = Field(default_factory=RiskFlags)

    @field_validator("themes")
    @classmethod
    def _themes_nonempty(cls, v: list[str]) -> list[str]:
        cleaned = [t.strip() for t in v if t.strip()]
        return cleaned or ["general"]


class EntryAnalysisOut(BaseModel):
    id: str
    entry_id: str
    user_id: str
    language: Language
    emotions: list[Emotion]
    themes: list[str]
    pillar_weights: dict
    pillar_scores: dict
    reflection: str
    recommendations: dict
    signals: dict
    rationale_summary: str
    risk_flags: dict
