from fastapi import APIRouter

from app.schemas.logs import SearchLogsRequest, SearchLogsResponse
from app.services.logs import LogService

router = APIRouter(prefix='/api/v1/logs', tags=['logs'])
service = LogService()


@router.post('/search', response_model=SearchLogsResponse)
def search_logs(request: SearchLogsRequest) -> SearchLogsResponse:
    return service.search(request)
