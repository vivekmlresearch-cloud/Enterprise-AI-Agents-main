from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy.orm import Session

from ..config import settings
from ..db.session import save_email_audit
from .guardrails import GuardrailService

logger = logging.getLogger(__name__)


class EmailAgent:
    def __init__(self) -> None:
        self.guardrails = GuardrailService()

    def send(self, session: Session, run_id: str, result: dict) -> bool:
        recipient = settings.email_to.strip()
        if not settings.email_enabled or not recipient:
            logger.info("Email disabled or recipient missing; skipping email for %s", result["ticker"])
            return False
        if settings.send_email_only_for_buy and result.get("verdict") != "BUY":
            logger.info("Email restricted to BUY verdicts; skipping %s", result["ticker"])
            return False

        subject = f"[{result['verdict']}] Stock alert for {result['ticker']}"
        body = self._render_body(result)
        body = self.guardrails.redact(body)

        msg = MIMEMultipart()
        msg["From"] = settings.email_from
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(settings.email_host, settings.email_port, timeout=30) as server:
                server.starttls()
                if settings.email_username:
                    server.login(settings.email_username, settings.email_password)
                server.sendmail(settings.email_from, [recipient], msg.as_string())
            save_email_audit(session, run_id, recipient, result["ticker"], True)
            return True
        except Exception as exc:
            logger.exception("Email send failed")
            save_email_audit(session, run_id, recipient, result["ticker"], False, str(exc))
            return False

    def _render_body(self, result: dict) -> str:
        reasons = "\n- ".join([""] + result.get("reasons", []))
        risks = "\n- ".join([""] + result.get("risks", []))
        return f"""Stock: {result['ticker']}
Verdict: {result['verdict']}
Technical Score: {result['technical_score']}
Macro Score: {result['macro_score']}
Final Score: {result['final_score']}
Confidence: {result['confidence']}

Today Price Summary:
{result.get('today_price_summary', '')}

Macro Summary:
{result.get('macro_summary', '')}

Reasons:{reasons}

Risks:{risks}

Disclaimer: This is a model-assisted signal and not guaranteed financial advice.
"""
