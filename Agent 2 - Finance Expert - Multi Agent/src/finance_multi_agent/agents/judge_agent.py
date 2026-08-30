from __future__ import annotations

from ..config import settings
from ..llm.google_gemma import build_llm_client
from ..state import GraphState


SYSTEM_PROMPT = """You are a financial signal judge.
You do not give absolute financial advice. You synthesize evidence from technical and macro analysis.
Return valid JSON with keys: final_score, verdict, confidence, reasons, risks.
Verdict must be one of BUY, WATCH, AVOID.
Use the provided deterministic thresholds as anchors.
"""


def run(state: GraphState) -> GraphState:
    llm = build_llm_client(model_name=settings.judge_model_name)
    judge_results = {}
    for ticker in state.get("tickers", []):
        tech = state.get("technical_results", {}).get(ticker, {})
        macro = state.get("macro_results", {}).get(ticker, {})
        deterministic = round(0.65 * float(tech.get("score", 0)) + 0.35 * float(macro.get("score", 50)), 2)
        deterministic_verdict = _verdict_from_score(deterministic)
        user_prompt = (
            f"Ticker: {ticker}\n"
            f"Technical score: {tech.get('score', 0)}\n"
            f"Technical signals: {tech.get('signals', [])}\n"
            f"Technical risks: {tech.get('risks', [])}\n"
            f"Today price summary: {tech.get('today_price_summary', '')}\n"
            f"Macro score: {macro.get('score', 50)}\n"
            f"Macro summary: {macro.get('summary', '')}\n"
            f"Macro factors: {macro.get('factors', [])}\n"
            f"Macro risks: {macro.get('risks', [])}\n"
            f"Deterministic anchor score: {deterministic}\n"
            f"Deterministic anchor verdict: {deterministic_verdict}\n"
            "Return a conservative final judgment close to the deterministic anchor unless strong evidence suggests otherwise."
        )
        llm_json = llm.invoke_json(SYSTEM_PROMPT, user_prompt)
        final_score = _bounded_float(llm_json.get("final_score"), deterministic)
        verdict = llm_json.get("verdict", _verdict_from_score(final_score))
        if verdict not in {"BUY", "WATCH", "AVOID"}:
            verdict = _verdict_from_score(final_score)
        confidence = max(0.0, min(1.0, _bounded_float(llm_json.get("confidence"), 0.7)))
        reasons = llm_json.get("reasons", []) or tech.get("signals", [])[:2] + macro.get("factors", [])[:2]
        risks = llm_json.get("risks", []) or tech.get("risks", [])[:2] + macro.get("risks", [])[:2]
        judge_results[ticker] = {
            "ticker": ticker,
            "technical_score": round(float(tech.get("score", 0)), 2),
            "macro_score": round(float(macro.get("score", 50)), 2),
            "final_score": round(float(final_score), 2),
            "verdict": verdict,
            "confidence": round(float(confidence), 2),
            "reasons": reasons[:6],
            "risks": risks[:6],
            "indicator_snapshot": tech.get("indicator_snapshot", {}),
            "macro_summary": macro.get("summary", ""),
            "today_price_summary": tech.get("today_price_summary", ""),
        }
    return {"judge_results": judge_results}


def _verdict_from_score(score: float) -> str:
    if score >= settings.buy_threshold:
        return "BUY"
    if score >= settings.watch_threshold:
        return "WATCH"
    return "AVOID"


def _bounded_float(value, default: float) -> float:
    try:
        return max(0.0, min(100.0 if default > 1 else 1.0, float(value)))
    except Exception:
        return default
