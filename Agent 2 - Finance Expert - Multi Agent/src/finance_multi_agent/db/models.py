from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(128), index=True)
    ticker: Mapped[str] = mapped_column(String(32), index=True)
    verdict: Mapped[str] = mapped_column(String(16), index=True)
    technical_score: Mapped[float] = mapped_column(Float)
    macro_score: Mapped[float] = mapped_column(Float)
    final_score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    reasons_json: Mapped[str] = mapped_column(Text)
    risks_json: Mapped[str] = mapped_column(Text)
    indicator_snapshot_json: Mapped[str] = mapped_column(Text)
    macro_summary: Mapped[str] = mapped_column(Text)
    today_price_summary: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StateSnapshot(Base):
    __tablename__ = "state_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(128), index=True)
    node_name: Mapped[str] = mapped_column(String(64), index=True)
    state_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_name: Mapped[str] = mapped_column(String(128), index=True)
    accuracy: Mapped[float] = mapped_column(Float)
    buy_precision: Mapped[float] = mapped_column(Float)
    watch_precision: Mapped[float] = mapped_column(Float)
    avoid_precision: Mapped[float] = mapped_column(Float)
    metrics_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EmailAudit(Base):
    __tablename__ = "email_audit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(128), index=True)
    recipient: Mapped[str] = mapped_column(String(256))
    ticker: Mapped[str] = mapped_column(String(32), index=True)
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
