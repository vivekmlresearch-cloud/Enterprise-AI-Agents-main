from __future__ import annotations

from ..state import GraphState
from ..utils.file_parser import parse_stock_file


def run(state: GraphState) -> GraphState:
    tickers, invalid = parse_stock_file(state["stocks_file"])
    return {
        "tickers": tickers,
        "invalid_tickers": invalid,
    }
