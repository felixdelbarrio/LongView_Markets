from __future__ import annotations

from typing import Any

from app.calculations.calculation_engine import OperationalCalculationEngine


class ForecastService:
    def instrument(self, ticker: str, prices: list[dict[str, Any]]) -> dict[str, Any]:
        return OperationalCalculationEngine().forecast_instrument(ticker, prices)

    def portfolio(self, valuation: dict[str, Any]) -> dict[str, Any]:
        return OperationalCalculationEngine().forecast_portfolio(valuation)
