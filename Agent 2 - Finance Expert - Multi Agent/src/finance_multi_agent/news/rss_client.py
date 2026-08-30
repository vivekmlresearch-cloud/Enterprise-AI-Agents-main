from __future__ import annotations

import urllib.parse
from datetime import datetime, timedelta, timezone

import feedparser

from ..config import settings


class RSSNewsClient:
    def __init__(self) -> None:
        self.lookback = settings.news_lookback_days

    def fetch_market_news(self, ticker: str) -> list[dict]:
        queries = [
            f"{ticker} India stock",
            "NIFTY India stock market",
            "Sensex India market outlook",
            "global markets risk sentiment India",
        ]
        articles: list[dict] = []
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.lookback)

        for query in queries:
            encoded = urllib.parse.quote(query)
            feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded}&hl=en-IN&gl=IN&ceid=IN:en")
            for entry in feed.entries[:8]:
                published = _parse_date(getattr(entry, "published", ""))
                if published and published < cutoff:
                    continue
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": published.isoformat() if published else None,
                    "summary": entry.get("summary", ""),
                    "source": entry.get("source", {}).get("title") if isinstance(entry.get("source"), dict) else "rss",
                })
        dedup = {}
        for a in articles:
            key = (a["title"], a["link"])
            dedup[key] = a
        return list(dedup.values())[:20]


def _parse_date(value: str):
    for fmt in ["%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"]:
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    return None
