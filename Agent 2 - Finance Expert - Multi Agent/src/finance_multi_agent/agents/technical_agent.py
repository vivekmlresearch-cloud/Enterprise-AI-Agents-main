from __future__ import annotations

import pandas as pd

from ..data.indicators import compute_indicators
from ..state import GraphState


def run(state: GraphState) -> GraphState:
    results = {}
    for ticker, payload in state.get("raw_market_data", {}).items():
        history = pd.DataFrame(payload.get("history", []))
        if history.empty:
            results[ticker] = {
                "score": 0,
                "signals": [],
                "risks": ["No market data available."],
                "indicator_snapshot": {},
                "today_price_summary": "No data available.",
            }
            continue
        if "Date" in history.columns:
            history["Date"] = pd.to_datetime(history["Date"])
            history = history.sort_values("Date")
        elif "Datetime" in history.columns:
            history["Datetime"] = pd.to_datetime(history["Datetime"])
            history = history.sort_values("Datetime")
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            history[col] = pd.to_numeric(history[col], errors="coerce")
        history = history.dropna(subset=["Open", "High", "Low", "Close"])
        try:
            indicator_result = compute_indicators(history)
            results[ticker] = {
                "score": indicator_result.score,
                "signals": indicator_result.signals,
                "risks": indicator_result.risks,
                "indicator_snapshot": indicator_result.latest,
                "today_price_summary": indicator_result.summary,
            }
        except Exception as exc:
            results[ticker] = {
                "score": 0,
                "signals": [],
                "risks": [f"Technical analysis failed: {exc}"],
                "indicator_snapshot": {},
                "today_price_summary": "Technical analysis unavailable.",
            }
    return {"technical_results": results}
