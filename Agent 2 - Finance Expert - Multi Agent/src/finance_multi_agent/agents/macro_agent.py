from __future__ import annotations

from collections import Counter

from ..config import settings
from ..llm.google_gemma import build_llm_client
from ..news.rss_client import RSSNewsClient
from ..state import GraphState

POSITIVE = {"gain", "up", "growth", "beat", "rally", "surge", "approval", "expansion", "strong"}
NEGATIVE = {"drop", "down", "fall", "miss", "crisis", "war", "tariff", "risk", "slump", "inflation"}


SYSTEM_PROMPT = """You are a macro market analyst for Indian equities.
Return valid JSON with keys: summary, factors, risks, macro_score.
Focus on India market context, company-specific relevance, and recent global risk signals.
Score from 0 to 100 where 50 is neutral, above 65 is constructive, below 40 is risk-off.
"""


def run(state: GraphState) -> GraphState:
    client = RSSNewsClient()
    llm = build_llm_client(model_name=settings.macro_model_name)
    results = {}

    for ticker in state.get("tickers", []):
        articles = client.fetch_market_news(ticker)
        fallback = _deterministic_macro_score(articles)
        user_prompt = (
            f"Ticker: {ticker}\n"
            f"Recent articles: {articles[:12]}\n"
            f"Deterministic score hint: {fallback['score']}\n"
            "Provide a concise macro summary relevant to a near-term stock decision."
        )
        llm_json = llm.invoke_json(SYSTEM_PROMPT, user_prompt)
        score = llm_json.get("macro_score", fallback["score"])
        try:
            score = float(score)
        except Exception:
            score = float(fallback["score"])
        score = max(0.0, min(100.0, score))
        results[ticker] = {
            "score": score,
            "summary": llm_json.get("summary", fallback["summary"]),
            "factors": llm_json.get("factors", fallback["factors"]),
            "risks": llm_json.get("risks", fallback["risks"]),
            "articles_used": articles[:12],
        }
    return {"macro_results": results}


def _deterministic_macro_score(articles: list[dict]) -> dict:
    tokens = []
    for article in articles:
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        tokens.extend(text.split())
    counts = Counter(tokens)
    pos = sum(counts.get(word, 0) for word in POSITIVE)
    neg = sum(counts.get(word, 0) for word in NEGATIVE)
    score = 50 + min(20, pos * 2) - min(20, neg * 2)
    factors = []
    risks = []
    if pos > 0:
        factors.append("Recent headlines show constructive market language and positive sentiment markers.")
    if neg > 0:
        risks.append("Recent headlines include explicit risk-off or negative sentiment markers.")
    summary = "Macro sentiment fallback based on recent headline keyword balance."
    return {"score": max(0, min(100, score)), "summary": summary, "factors": factors, "risks": risks}
