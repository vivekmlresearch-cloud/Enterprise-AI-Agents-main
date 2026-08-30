from __future__ import annotations

import logging
import sys
from typing import Optional

from .config import settings


def setup_logging(level: Optional[str] = None) -> None:
    logging.basicConfig(
        level=getattr(logging, (level or settings.log_level).upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
