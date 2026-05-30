from __future__ import annotations

from app.analytics.calculation_engine import CalculationEngine
from app.providers.mock_provider import MockProvider


def get_provider() -> MockProvider:
    return MockProvider()


def get_calculation_engine() -> CalculationEngine:
    return CalculationEngine()
