from __future__ import annotations

from app.schemas.common import Evidence, LogRecord


class HistoryService:
    def find_similar_incidents(self, service: str, logs: list[LogRecord]) -> list[Evidence]:
        if not logs:
            return []
        return [
            Evidence(
                source='incident-memory',
                title=f'Prior issue pattern for {service}',
                content='A similar sequence of repeated timeout and connection reset messages previously followed a dependency degradation.',
                score=0.82,
            )
        ]

    def relevant_runbooks(self, service: str) -> list[Evidence]:
        return [
            Evidence(
                source='runbook',
                title=f'{service} incident response runbook',
                content='Validate upstream dependency health, compare deploy version, and verify queue depth before scaling or restarting.',
                score=0.91,
            )
        ]
