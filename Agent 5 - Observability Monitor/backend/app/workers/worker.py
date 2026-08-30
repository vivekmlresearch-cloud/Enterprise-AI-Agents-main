from __future__ import annotations

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from app.core.config import get_settings
from app.workers import activities
from app.workers.workflows import ActionWorkflow


async def main() -> None:
    settings = get_settings()
    client = await Client.connect(settings.temporal_host, namespace=settings.temporal_namespace)
    worker = Worker(
        client,
        task_queue='observability-actions',
        workflows=[ActionWorkflow],
        activities=[
            activities.send_email_activity,
            activities.send_webhook_activity,
            activities.slack_activity,
            activities.pagerduty_activity,
        ],
    )
    await worker.run()


if __name__ == '__main__':
    asyncio.run(main())
