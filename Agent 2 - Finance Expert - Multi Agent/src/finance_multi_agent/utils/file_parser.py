from __future__ import annotations

from pathlib import Path


def parse_stock_file(path: str) -> tuple[list[str], list[str]]:
    content = Path(path).read_text(encoding="utf-8").strip()
    raw = [token.strip().upper() for token in content.split(",") if token.strip()]
    unique = []
    seen = set()
    invalid = []
    for ticker in raw:
        if ticker in seen:
            continue
        seen.add(ticker)
        if "." not in ticker or not ticker.split(".")[-1] in {"NS", "BO"}:
            invalid.append(ticker)
            continue
        unique.append(ticker)
    return unique, invalid
