from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class TechnicalResult(BaseModel):
    ticker: str
    score: float = Field(ge=0, le=100)
    signals: list[str]
    risks: list[str]
    indicator_snapshot: dict[str, float | str | None]
    today_price_summary: str


class MacroResult(BaseModel):
    ticker: str
    score: float = Field(ge=0, le=100)
    summary: str
    factors: list[str]
    risks: list[str]
    articles_used: list[dict]


class JudgeResult(BaseModel):
    ticker: str
    technical_score: float = Field(ge=0, le=100)
    macro_score: float = Field(ge=0, le=100)
    final_score: float = Field(ge=0, le=100)
    verdict: str
    confidence: float = Field(ge=0, le=1)
    reasons: list[str]
    risks: list[str]
    indicator_snapshot: dict
    macro_summary: str
    today_price_summary: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
