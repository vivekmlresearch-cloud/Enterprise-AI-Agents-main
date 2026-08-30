from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from app.workers import activities


@workflow.defn
class ActionWorkflow:
    @workflow.run
    async def run(self, payload: dict) -> str:
        action_type = payload['action_type']
        if action_type == 'email':
            return await workflow.execute_activity(
                activities.send_email_activity,
                payload,
                start_to_close_timeout=timedelta(seconds=30),
            )
        if action_type == 'slack':
            return await workflow.execute_activity(
                activities.slack_activity,
                payload,
                start_to_close_timeout=timedelta(seconds=30),
            )
        if action_type == 'pagerduty':
            return await workflow.execute_activity(
                activities.pagerduty_activity,
                payload,
                start_to_close_timeout=timedelta(seconds=30),
            )
        return await workflow.execute_activity(
            activities.send_webhook_activity,
            payload,
            start_to_close_timeout=timedelta(seconds=30),
        )
