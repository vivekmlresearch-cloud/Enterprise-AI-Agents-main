from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class MarketBundle:
    ticker: str
    history: pd.DataFrame
    info: dict
    latest_price: float | None
    previous_close: float | None


class YahooFinanceClient:
    def fetch(self, ticker: str, period: str = "6mo", interval: str = "1d") -> MarketBundle:
        tk = yf.Ticker(ticker)
        history = tk.history(period=period, interval=interval, auto_adjust=False)
        history = history.dropna(how="all")
        info = {}
        latest_price = None
        previous_close = None

        if not history.empty:
            latest_price = float(history["Close"].iloc[-1])
            if len(history) > 1:
                previous_close = float(history["Close"].iloc[-2])

        try:
            info = dict(tk.fast_info) if tk.fast_info else {}
        except Exception as exc:
            logger.warning("fast_info unavailable for %s: %s", ticker, exc)
            info = {}

        return MarketBundle(
            ticker=ticker,
            history=history,
            info=info,
            latest_price=latest_price,
            previous_close=previous_close,
        )

    def fetch_many(self, tickers: list[str], period: str = "6mo", interval: str = "1d") -> dict[str, MarketBundle]:
        return {ticker: self.fetch(ticker, period=period, interval=interval) for ticker in tickers}
