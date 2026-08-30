from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jsonl(path: str) -> list[dict[str, Any]]:
    rows = []
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows
