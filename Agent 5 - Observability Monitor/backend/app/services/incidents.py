from __future__ import annotations

from datetime import datetime

from app.orchestration.graph import build_graph
from app.schemas.incidents import AnalyzeIncidentRequest, AnalyzeIncidentResponse
from app.services.clickhouse import ClickHouseRepository


class IncidentService:
    def __init__(self) -> None:
        self.repo = ClickHouseRepository()
        self.graph = build_graph()

    async def analyze(self, request: AnalyzeIncidentRequest) -> AnalyzeIncidentResponse:
        logs = self.repo.recent_error_window(request.service, request.environment, request.window_minutes)
        if not logs:
            return AnalyzeIncidentResponse.empty(request.service, request.environment)
        state = {
            'service': request.service,
            'environment': request.environment,
            'logs': logs,
        }
        result = await self.graph.ainvoke(state)
        return AnalyzeIncidentResponse(
            generated_at=datetime.utcnow(),
            service=request.service,
            environment=request.environment,
            summary=result['summary'],
            related_logs=logs[:50],
        )
