from datetime import datetime, timedelta
import random

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / 'backend'))

from app.schemas.common import LogRecord
from app.services.clickhouse import ClickHouseRepository


SERVICES = ['checkout-service', 'payments-service', 'catalog-service']
MESSAGES = [
    'upstream timeout while calling payment-gateway',
    'connection reset by peer from inventory service',
    'queue depth warning exceeded threshold',
    'database latency increased beyond baseline',
    'healthcheck failed for dependency endpoint',
]


def main() -> None:
    repo = ClickHouseRepository()
    now = datetime.utcnow()
    rows = []
    for minute_offset in range(120):
        for _ in range(random.randint(1, 6)):
            service = random.choice(SERVICES)
            severity = random.choice(['INFO', 'WARN', 'ERROR'])
            if service == 'checkout-service' and minute_offset < 30:
                severity = random.choice(['WARN', 'ERROR'])
            rows.append(
                LogRecord(
                    timestamp=now - timedelta(minutes=minute_offset),
                    service=service,
                    severity=severity,
                    message=random.choice(MESSAGES),
                    environment='prod',
                    host='node-a',
                    container=f'{service}-container',
                    trace_id=f'trace-{minute_offset}',
                    metadata={'source': 'seed'},
                )
            )
    repo.insert_logs(rows)
    print(f'Seeded {len(rows)} log records')


if __name__ == '__main__':
    main()
