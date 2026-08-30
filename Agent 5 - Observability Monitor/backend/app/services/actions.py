from __future__ import annotations

from temporalio.client import Client

from app.core.config import get_settings
from app.schemas.actions import ExecuteActionRequest, ExecuteActionResponse
from app.workers.workflows import ActionWorkflow


class ActionService:
    async def execute(self, request: ExecuteActionRequest) -> ExecuteActionResponse:
        settings = get_settings()
        client = await Client.connect(settings.temporal_host, namespace=settings.temporal_namespace)
        workflow_id = f'action-{request.action_type}-{request.title.lower().replace(" ", "-")}'
        await client.start_workflow(
            ActionWorkflow.run,
            request.model_dump(),
            id=workflow_id,
            task_queue='observability-actions',
        )
        return ExecuteActionResponse(
            detail=f'{request.action_type} action accepted for execution',
            workflow_id=workflow_id,
            metadata={'requires_approval': request.requires_approval},
        )
