from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import LogRecord


class SearchLogsRequest(BaseModel):
    service: Optional[str] = None
    environment: str = 'prod'
    severity: Optional[List[str]] = None
    query: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)


class SearchLogsResponse(BaseModel):
    records: List[LogRecord]
