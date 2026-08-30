from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class ForecastItem(BaseModel):
    service: str
    metric: str
    likely_event: str
    confidence: float
    horizon_minutes: int
    rationale: str
    generated_at: datetime


class ForecastResponse(BaseModel):
    items: List[ForecastItem] = Field(default_factory=list)
