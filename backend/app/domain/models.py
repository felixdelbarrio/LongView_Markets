from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class Instrument(BaseModel):
    ticker: str
    name: str
    isin: str | None = None
    market: str
    exchange: str
    country: str
    currency: str
    sector: str
    industry: str
    provider: str
    data_quality_score: float = Field(ge=0, le=100)
    last_updated_at: datetime


class DailyPrice(BaseModel):
    date: date
    ticker: str
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float
    volume: int
    currency: str
    provider: str
    ingested_at: datetime
    quality_score: float = Field(ge=0, le=100)


class Dividend(BaseModel):
    ticker: str
    ex_dividend_date: date
    payment_date: date
    amount: float
    currency: str
    dividend_type: str
    provider: str
    ingested_at: datetime
    quality_score: float = Field(ge=0, le=100)


class NewsItem(BaseModel):
    id: str
    headline: str
    summary: str
    source: str
    url: HttpUrl | str
    published_at: datetime
    tickers: list[str]
    sentiment: str
    confidence: float = Field(ge=0, le=1)
    provider: str


class PortfolioTransaction(BaseModel):
    id: str
    portfolio_id: str
    ticker: str
    transaction_type: str
    quantity: float
    price: float
    currency: str
    fees: float = 0
    taxes: float = 0
    date: date
    notes: str = ""


class Insight(BaseModel):
    id: str
    ticker: str
    title: str
    category: str
    severity: str
    explanation: str
    evidence: dict[str, Any]
    confidence: float = Field(ge=0, le=1)
    generated_at: datetime
    data_sources: list[str]


class Forecast(BaseModel):
    ticker: str
    model_name: str
    model_version: str
    generated_at: datetime
    horizon_days: int
    scenario: str
    expected_path: list[dict[str, Any]]
    confidence_interval_low: float
    confidence_interval_high: float
    confidence: float = Field(ge=0, le=1)
    limitations: list[str]


class Watchlist(BaseModel):
    id: str
    name: str
    description: str
    items: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class DecisionJournalEntry(BaseModel):
    id: str
    ticker: str
    decision_type: str
    thesis: str
    risks: list[str]
    expected_horizon: str
    entry_price: float
    snapshot_metrics: dict[str, Any]
    status: str
    review_date: date
    created_at: datetime
    updated_at: datetime
