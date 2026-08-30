from datetime import datetime, timedelta
from typing import List

from pydantic import BaseModel, Field

from app.schemas.common import IncidentSummary, LogRecord


class AnalyzeIncidentRequest(BaseModel):
    service: str
    environment: str = 'prod'
    window_minutes: int = 30
    severity_filter: List[str] = Field(default_factory=lambda: ['ERROR', 'WARN'])


class AnalyzeIncidentResponse(BaseModel):
    generated_at: datetime
    service: str
    environment: str
    summary: IncidentSummary
    related_logs: List[LogRecord] = Field(default_factory=list)

    @classmethod
    def empty(cls, service: str, environment: str) -> 'AnalyzeIncidentResponse':
        now = datetime.utcnow()
        return cls(
            generated_at=now,
            service=service,
            environment=environment,
            summary=IncidentSummary(
                title=f'No anomaly detected for {service}',
                severity='INFO',
                summary='No critical anomaly was detected in the selected time window.',
            ),
            related_logs=[],
        )
