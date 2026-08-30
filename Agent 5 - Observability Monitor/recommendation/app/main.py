from datetime import datetime

import clickhouse_connect
from fastapi import FastAPI
from pydantic import BaseModel

from app.config import get_settings

app = FastAPI(title='Recommendation Service')


class GenerateResponse(BaseModel):
    inserted: int


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'recommendation'}


@app.post('/generate', response_model=GenerateResponse)
def generate_predictions() -> GenerateResponse:
    settings = get_settings()
    client = clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        username=settings.clickhouse_username,
        password=settings.clickhouse_password,
        database=settings.clickhouse_database,
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
    rows = [
        [datetime.utcnow(), 'checkout-service', 'error_rate', 'Likely next: timeout spike if dependency health does not recover', 0.74, 20, 'Based on recent error concentration and historical timeout sequences.'],
        [datetime.utcnow(), 'payments-service', 'latency_p95', 'Likely next: latency increase under sustained queue depth', 0.67, 30, 'Trend-based forecast from recent warning and throughput patterns.'],
    ]
    client.insert(
        'forecasts',
        rows,
        column_names=['generated_at', 'service', 'metric', 'likely_event', 'confidence', 'horizon_minutes', 'rationale'],
    )
    return GenerateResponse(inserted=len(rows))
