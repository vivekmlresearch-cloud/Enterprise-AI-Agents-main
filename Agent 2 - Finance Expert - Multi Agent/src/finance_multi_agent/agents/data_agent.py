from __future__ import annotations

import logging

from ..data.yahoo_client import YahooFinanceClient
from ..state import GraphState
from ..utils.serialization import to_jsonable

logger = logging.getLogger(__name__)


def run(state: GraphState) -> GraphState:
    client = YahooFinanceClient()
    bundles = client.fetch_many(state.get("tickers", []))
    raw_market_data = {}
    for ticker, bundle in bundles.items():
        raw_market_data[ticker] = {
            "history": to_jsonable(bundle.history.reset_index().to_dict(orient="records")),
            "latest_price": bundle.latest_price,
            "previous_close": bundle.previous_close,
            "info": to_jsonable(bundle.info),
        }
    return {"raw_market_data": raw_market_data}
