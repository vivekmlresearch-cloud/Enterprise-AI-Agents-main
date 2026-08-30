from fastapi import APIRouter

from app.schemas.incidents import AnalyzeIncidentRequest, AnalyzeIncidentResponse
from app.services.incidents import IncidentService

router = APIRouter(prefix='/api/v1/incidents', tags=['incidents'])
service = IncidentService()


@router.post('/analyze', response_model=AnalyzeIncidentResponse)
async def analyze_incident(request: AnalyzeIncidentRequest) -> AnalyzeIncidentResponse:
    return await service.analyze(request)
