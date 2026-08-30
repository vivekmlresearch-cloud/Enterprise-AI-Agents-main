from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable, List

import clickhouse_connect

from app.core.config import get_settings
from app.schemas.common import LogRecord
from app.schemas.forecast import ForecastItem


class ClickHouseRepository:
    def __init__(self) -> None:
        self.client = None
        self._ensure_client()

    def _ensure_client(self):
        if self.client is None:
            settings = get_settings()
            self.client = clickhouse_connect.get_client(
                host=settings.clickhouse_host,
                port=settings.clickhouse_port,
                username=settings.clickhouse_username,
                password=settings.clickhouse_password,
                database=settings.clickhouse_database,
            )
            self._ensure_schema()
        return self.client

    def _ensure_schema(self) -> None:
        client = self.client
        client.command(
            '''
            CREATE TABLE IF NOT EXISTS logs (
                timestamp DateTime,
                service String,
                severity String,
                message String,
                environment String,
                host Nullable(String),
                container Nullable(String),
                trace_id Nullable(String),
                metadata String
            ) ENGINE = MergeTree
            ORDER BY (service, environment, timestamp)
            '''
        )
        client.command(
            '''
            CREATE TABLE IF NOT EXISTS forecasts (
                generated_at DateTime,
                service String,
                metric String,
                likely_event String,
                confidence Float64,
                horizon_minutes UInt32,
                rationale String
            ) ENGINE = MergeTree
            ORDER BY (service, generated_at)
            '''
        )

    def insert_logs(self, records: Iterable[LogRecord]) -> None:
        client = self._ensure_client()
        rows = [
            [
                record.timestamp,
                record.service,
                record.severity,
                record.message,
                record.environment,
                record.host,
                record.container,
                record.trace_id,
                str(record.metadata),
            ]
            for record in records
        ]
        if rows:
            client.insert(
                'logs',
                rows,
                column_names=[
                    'timestamp',
                    'service',
                    'severity',
                    'message',
                    'environment',
                    'host',
                    'container',
                    'trace_id',
                    'metadata',
                ],
            )

    def search_logs(
        self,
        service: str | None = None,
        environment: str = 'prod',
        severity: list[str] | None = None,
        query: str | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 100,
    ) -> List[LogRecord]:
        client = self._ensure_client()
        clauses = ['environment = %(environment)s']
        params: dict[str, object] = {'environment': environment, 'limit': limit}
        if service:
            clauses.append('service = %(service)s')
            params['service'] = service
        if severity:
            values = ', '.join([f"'{s}'" for s in severity])
            clauses.append(f'severity IN ({values})')
        if query:
            clauses.append('message ILIKE %(query)s')
            params['query'] = f'%{query}%'
        if start:
            clauses.append('timestamp >= %(start)s')
            params['start'] = start
        if end:
            clauses.append('timestamp <= %(end)s')
            params['end'] = end
        sql = f'''
            SELECT timestamp, service, severity, message, environment, host, container, trace_id
            FROM logs
            WHERE {' AND '.join(clauses)}
            ORDER BY timestamp DESC
            LIMIT %(limit)s
        '''
        result = client.query(sql, parameters=params)
        return [
            LogRecord(
                timestamp=row[0],
                service=row[1],
                severity=row[2],
                message=row[3],
                environment=row[4],
                host=row[5],
                container=row[6],
                trace_id=row[7],
                metadata={},
            )
            for row in result.result_rows
        ]

    def recent_error_window(self, service: str, environment: str, window_minutes: int) -> List[LogRecord]:
        end = datetime.utcnow()
        start = end - timedelta(minutes=window_minutes)
        return self.search_logs(
            service=service,
            environment=environment,
            severity=['ERROR', 'WARN'],
            start=start,
            end=end,
            limit=500,
        )

    def count_recent_errors(self, service: str, environment: str, window_minutes: int) -> int:
        client = self._ensure_client()
        sql = f'''
            SELECT count()
            FROM logs
            WHERE service = %(service)s AND environment = %(environment)s
              AND severity IN ('ERROR', 'WARN')
              AND timestamp >= now() - INTERVAL {int(window_minutes)} MINUTE
        '''
        result = client.query(sql, parameters={'service': service, 'environment': environment})
        return int(result.first_row[0]) if result.first_row else 0

    def write_forecasts(self, items: list[ForecastItem]) -> None:
        client = self._ensure_client()
        rows = [
            [
                item.generated_at,
                item.service,
                item.metric,
                item.likely_event,
                item.confidence,
                item.horizon_minutes,
                item.rationale,
            ]
            for item in items
        ]
        if rows:
            client.insert(
                'forecasts',
                rows,
                column_names=[
                    'generated_at',
                    'service',
                    'metric',
                    'likely_event',
                    'confidence',
                    'horizon_minutes',
                    'rationale',
                ],
            )

    def latest_forecasts(self, limit: int = 20) -> list[ForecastItem]:
        client = self._ensure_client()
        result = client.query(
            '''
            SELECT generated_at, service, metric, likely_event, confidence, horizon_minutes, rationale
            FROM forecasts
            ORDER BY generated_at DESC
            LIMIT %(limit)s
            ''',
            parameters={'limit': limit},
        )
        return [
            ForecastItem(
                generated_at=row[0],
                service=row[1],
                metric=row[2],
                likely_event=row[3],
                confidence=row[4],
                horizon_minutes=row[5],
                rationale=row[6],
            )
            for row in result.result_rows
        ]
