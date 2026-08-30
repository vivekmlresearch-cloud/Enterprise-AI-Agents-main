from __future__ import annotations

from app.schemas.logs import SearchLogsRequest, SearchLogsResponse
from app.services.clickhouse import ClickHouseRepository


class LogService:
    def __init__(self) -> None:
        self.repo = ClickHouseRepository()

    def search(self, request: SearchLogsRequest) -> SearchLogsResponse:
        records = self.repo.search_logs(
            service=request.service,
            environment=request.environment,
            severity=request.severity,
            query=request.query,
            start=request.start,
            end=request.end,
            limit=request.limit,
        )
        return SearchLogsResponse(records=records)
