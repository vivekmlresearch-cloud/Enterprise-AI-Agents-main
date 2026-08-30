from __future__ import annotations

import orjson
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import settings
from ..utils.serialization import to_jsonable
from .base import Base
from .models import AnalysisRun, EmailAudit, EvaluationRun, StateSnapshot


engine = create_engine(settings.db_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def save_snapshot(session: Session, run_id: str, node_name: str, state: dict) -> None:
    row = StateSnapshot(run_id=run_id, node_name=node_name, state_json=orjson.dumps(to_jsonable(state)).decode())
    session.add(row)
    session.commit()


def save_analysis_result(session: Session, run_id: str, payload: dict) -> None:
    row = AnalysisRun(
        run_id=run_id,
        ticker=payload["ticker"],
        verdict=payload["verdict"],
        technical_score=payload["technical_score"],
        macro_score=payload["macro_score"],
        final_score=payload["final_score"],
        confidence=payload["confidence"],
        reasons_json=orjson.dumps(payload.get("reasons", [])).decode(),
        risks_json=orjson.dumps(payload.get("risks", [])).decode(),
        indicator_snapshot_json=orjson.dumps(to_jsonable(payload.get("indicator_snapshot", {}))).decode(),
        macro_summary=payload.get("macro_summary", ""),
        today_price_summary=payload.get("today_price_summary", ""),
    )
    session.add(row)
    session.commit()


def save_email_audit(session: Session, run_id: str, recipient: str, ticker: str, sent: bool, error_message: str | None = None) -> None:
    row = EmailAudit(run_id=run_id, recipient=recipient, ticker=ticker, sent=sent, error_message=error_message)
    session.add(row)
    session.commit()


def save_evaluation(session: Session, run_name: str, accuracy: float, buy_precision: float, watch_precision: float, avoid_precision: float, metrics: dict) -> None:
    row = EvaluationRun(
        run_name=run_name,
        accuracy=accuracy,
        buy_precision=buy_precision,
        watch_precision=watch_precision,
        avoid_precision=avoid_precision,
        metrics_json=orjson.dumps(metrics).decode(),
    )
    session.add(row)
    session.commit()
