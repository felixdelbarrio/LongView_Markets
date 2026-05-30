from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class CalculationMetadata(BaseModel):
    calculation_version: str
    calculated_at: datetime
    inputs_summary: dict[str, Any]
    data_sources: list[str]
    warnings: list[str] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)


class PortfolioValuationRequest(BaseModel):
    portfolio_id: str = "real"
    base_currency: str = "EUR"
    as_of: date | None = None


class PortfolioValuationResult(CalculationMetadata):
    portfolio_id: str
    base_currency: str
    total_market_value_base: float
    total_invested_base: float
    realized_pnl_base: float
    unrealized_pnl_base: float
    dividends_received_base: float
    fees_paid_base: float
    taxes_paid_base: float
    total_return_base: float
    total_return_pct: float
    daily_change_base: float
    daily_change_pct: float
    ytd_return_pct: float
    currency_exposure: list[dict[str, Any]]
    country_exposure: list[dict[str, Any]]
    sector_exposure: list[dict[str, Any]]
    top_positions: list[dict[str, Any]]
    risk_flags: list[str]
    positions: list[dict[str, Any]]


class PortfolioHistoryRequest(BaseModel):
    portfolio_id: str = "real"
    start: date | None = None
    end: date | None = None
    currency: str = "EUR"


class PortfolioHistoryResult(CalculationMetadata):
    portfolio_id: str
    currency: str
    history: list[dict[str, Any]]


class InstrumentPerformanceRequest(BaseModel):
    ticker: str
    portfolio_id: str = "real"
    start: date | None = None
    end: date | None = None
    currency: str = "EUR"


class InstrumentPerformanceResult(CalculationMetadata):
    ticker: str
    portfolio_id: str
    currency: str
    history: list[dict[str, Any]]


class ForecastRequest(BaseModel):
    ticker: str | None = None
    portfolio_id: str = "real"
    horizon_days: int = 180


class ForecastResult(CalculationMetadata):
    entity_type: str
    entity_id: str
    model_name: str
    model_version: str
    horizon_days: int
    scenarios: list[dict[str, Any]]
    confidence: float
    features_used: list[str]
    limitations: list[str]
    generative_context_used: bool


class FxConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str = "EUR"
    on_date: date | None = None


class FxConversionResult(CalculationMetadata):
    amount: float
    from_currency: str
    to_currency: str
    converted_amount: float
    fx_rate: float
    fx_rate_date: date
    data_kind: str
