from __future__ import annotations

from collections import Counter
from statistics import mean

from app.schemas.common import LogRecord


class AnomalyDetector:
    def detect(self, logs: list[LogRecord]) -> dict:
        if not logs:
            return {'is_anomalous': False, 'error_count': 0, 'top_patterns': []}
        messages = [record.message for record in logs]
        counts = Counter(messages)
        top_patterns = [{'message': msg, 'count': count} for msg, count in counts.most_common(5)]
        error_count = len(logs)
        severity = 'CRITICAL' if error_count >= 50 else 'HIGH' if error_count >= 20 else 'MEDIUM'
        return {
            'is_anomalous': error_count > 0,
            'error_count': error_count,
            'top_patterns': top_patterns,
            'severity': severity,
        }
