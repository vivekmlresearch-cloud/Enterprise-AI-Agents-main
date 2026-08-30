from __future__ import annotations

from typing import Any, Literal
from typing_extensions import TypedDict


Verdict = Literal["BUY", "WATCH", "AVOID", "ERROR"]


class StockDecision(TypedDict, total=False):
    ticker: str
    technical_score: float
    macro_score: float
    final_score: float
    verdict: Verdict
    confidence: float
    reasons: list[str]
    risks: list[str]
    indicator_snapshot: dict[str, Any]
    macro_summary: str
    today_price_summary: str


class GraphState(TypedDict, total=False):
    run_id: str
    thread_id: str
    stocks_file: str
    tickers: list[str]
    invalid_tickers: list[str]
    raw_market_data: dict[str, Any]
    technical_results: dict[str, Any]
    macro_results: dict[str, Any]
    judge_results: dict[str, StockDecision]
    alerts_sent: list[str]
    errors: list[str]
    metadata: dict[str, Any]
