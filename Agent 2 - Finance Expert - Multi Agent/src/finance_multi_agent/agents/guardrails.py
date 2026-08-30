from __future__ import annotations

import logging

from ..config import settings

logger = logging.getLogger(__name__)


class GuardrailService:
    def __init__(self) -> None:
        self.enabled = settings.enable_presidio
        self.analyzer = None
        self.anonymizer = None
        if self.enabled:
            try:
                from presidio_analyzer import AnalyzerEngine
                from presidio_anonymizer import AnonymizerEngine

                self.analyzer = AnalyzerEngine()
                self.anonymizer = AnonymizerEngine()
            except Exception as exc:
                logger.warning("Presidio unavailable, continuing without redaction: %s", exc)
                self.enabled = False

    def redact(self, text: str) -> str:
        if not text or not self.enabled or self.analyzer is None or self.anonymizer is None:
            return text
        try:
            results = self.analyzer.analyze(text=text, language="en")
            return self.anonymizer.anonymize(text=text, analyzer_results=results).text
        except Exception as exc:
            logger.warning("Redaction failed: %s", exc)
            return text
