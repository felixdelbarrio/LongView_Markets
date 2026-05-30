from __future__ import annotations

from pydantic import BaseModel


class ForecastRequest(BaseModel):
    ticker: str
    horizon_days: int = 90
