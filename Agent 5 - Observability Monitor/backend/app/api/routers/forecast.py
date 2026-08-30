from fastapi import APIRouter

from app.schemas.forecast import ForecastResponse
from app.services.forecast import ForecastService

router = APIRouter(prefix='/api/v1/forecast', tags=['forecast'])
service = ForecastService()


@router.get('/current', response_model=ForecastResponse)
def current_forecast() -> ForecastResponse:
    return service.current()
