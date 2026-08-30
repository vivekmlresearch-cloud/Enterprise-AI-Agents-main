from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Iterable


def stable_id(parts: Iterable[Any]) -> str:
    normalized = ["" if p is None else str(p).strip() for p in parts]
    blob = "||".join(normalized)
    digest = hashlib.sha256(blob.encode("utf-8")).digest()
    return str(uuid.UUID(bytes=digest[:16]))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def compact_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))