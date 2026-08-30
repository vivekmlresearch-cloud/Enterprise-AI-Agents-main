from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = 'ok'
    service: str


class TimeRange(BaseModel):
    start: datetime
    end: datetime


class ActionResult(BaseModel):
    accepted: bool = True
    workflow_id: Optional[str] = None
    detail: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    source: str
    title: str
    content: str
    score: float | None = None


class Recommendation(BaseModel):
    title: str
    detail: str
    confidence: float = 0.0
    requires_approval: bool = False


class LogRecord(BaseModel):
    timestamp: datetime
    service: str
    severity: str
    message: str
    environment: str = 'prod'
    host: Optional[str] = None
    container: Optional[str] = None
    trace_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IncidentSummary(BaseModel):
    title: str
    severity: str
    summary: str
    likely_causes: List[str] = Field(default_factory=list)
    what_may_happen_next: List[str] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
