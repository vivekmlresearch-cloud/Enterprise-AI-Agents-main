from __future__ import annotations

import json
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)


async def send_email_activity(payload: dict) -> str:
    settings = get_settings()
    recipient = payload.get('recipient') or 'ops@example.com'
    message = EmailMessage()
    message['From'] = settings.smtp_from
    message['To'] = recipient
    message['Subject'] = payload['title']
    message.set_content(payload['message'])
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.send_message(message)
    return f'email sent to {recipient}'


async def send_webhook_activity(payload: dict) -> str:
    logger.info('Webhook event: %s', json.dumps(payload))
    return 'webhook event recorded'


async def slack_activity(payload: dict) -> str:
    logger.info('Slack alert: %s', json.dumps(payload))
    return 'slack alert recorded'


async def pagerduty_activity(payload: dict) -> str:
    logger.info('PagerDuty event: %s', json.dumps(payload))
    return 'pagerduty event recorded'
