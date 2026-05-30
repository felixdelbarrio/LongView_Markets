from __future__ import annotations

from typing import Any

from app.analytics.calculation_engine import CalculationEngine


class PortfolioEngine:
    def __init__(self) -> None:
        self.calculation_engine = CalculationEngine()

    def summarize(
        self,
        transactions: list[dict[str, Any]],
        latest_prices: dict[str, dict[str, Any]],
        instruments: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self.calculation_engine.calculate_portfolio_metrics(transactions, latest_prices, instruments)
