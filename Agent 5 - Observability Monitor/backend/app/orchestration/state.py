from typing import Annotated, TypedDict

from app.schemas.common import Evidence, IncidentSummary, LogRecord, Recommendation


class IncidentState(TypedDict, total=False):
    service: str
    environment: str
    logs: list[LogRecord]
    anomaly: dict
    evidence: list[Evidence]
    llm_summary: str
    recommendations: list[Recommendation]
    summary: IncidentSummary
