from __future__ import annotations

from app.schemas.forecast import ForecastResponse
from app.services.clickhouse import ClickHouseRepository


class ForecastService:
    def __init__(self) -> None:
        self.repo = ClickHouseRepository()

    def current(self) -> ForecastResponse:
        return ForecastResponse(items=self.repo.latest_forecasts())
