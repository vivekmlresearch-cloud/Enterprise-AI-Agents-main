from fastapi import APIRouter

from app.schemas.actions import ExecuteActionRequest, ExecuteActionResponse
from app.services.actions import ActionService

router = APIRouter(prefix='/api/v1/actions', tags=['actions'])
service = ActionService()


@router.post('/execute', response_model=ExecuteActionResponse)
async def execute_action(request: ExecuteActionRequest) -> ExecuteActionResponse:
    return await service.execute(request)
