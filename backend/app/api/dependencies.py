from __future__ import annotations

from app.analytics.calculation_engine import CalculationEngine
from app.providers.yfinance_provider import Provider as YFinanceProvider


def get_provider() -> YFinanceProvider:
    return YFinanceProvider()


def get_calculation_engine() -> CalculationEngine:
    return CalculationEngine()
