from __future__ import annotations

from datetime import UTC, date, datetime

from app.analytics.explainability import explain_metric
from app.analytics.indicators import moving_average_signal
from app.analytics.metrics import get_metric_catalog
from app.analytics.risk import concentration_status
from app.core.errors import not_found, validation_error
from app.core.logging import get_logger
from app.core.security import mask_secrets, sanitize_text
from app.data_quality.validators import validate_ohlc
from app.dividends.dividend_fisher import simulate_capture
from app.domain.enums import DataKind, Severity, TransactionType
from app.domain.models import (
    DailyPrice,
    DecisionJournalEntry,
    Dividend,
    Forecast,
    Insight,
    Instrument,
    NewsItem,
    PortfolioTransaction,
    Watchlist,
)
from app.domain.value_objects import DataLineage, MetricDescription
from app.forecasting.models import ForecastRequest
from app.forecasting.scenarios import SCENARIOS
from app.news.news_engine import NewsEngine
from app.news.sentiment import sentiment_score
from app.portfolios.performance import benchmark_delta
from app.providers.dividend_provider import Provider as DividendProvider
from app.providers.mock_provider import MockProvider
from app.providers.news_provider import Provider as NewsProvider
from app.repositories import demo_repository
from app.repositories.dividend_repository import DividendRepository
from app.repositories.instrument_repository import InstrumentRepository
from app.repositories.metadata_repository import MetadataRepository
from app.repositories.news_repository import NewsRepository
from app.repositories.parquet_repository import ParquetRepository
from app.repositories.portfolio_repository import LocalRepository as PortfolioRepository
from app.repositories.price_repository import PriceRepository
from app.repositories.settings_repository import LocalRepository as SettingsRepository


def test_catalogs_and_utility_functions() -> None:
    assert get_metric_catalog()["cagr"]["label"] == "CAGR"
    assert explain_metric("unknown")["label"] == "unknown"
    assert moving_average_signal([float(index) for index in range(220)]) == "bullish"
    assert moving_average_signal([1.0, 2.0]) == "insufficient_history"
    assert concentration_status(80) == "high"
    assert concentration_status(60) == "medium"
    assert concentration_status(20) == "controlled"
    assert sanitize_text("<MSFT>") == "MSFT"
    assert mask_secrets("api_key=abcdef") == "api_key=***"
    assert not_found("missing").status_code == 404
    assert validation_error("bad").status_code == 422
    assert get_logger("longview.test").name == "longview.test"
    assert simulate_capture(100, 2)["central_result"] < 0
    assert benchmark_delta(10.5, 7.0) == 3.5
    assert sentiment_score("positive") > sentiment_score("negative")


def test_validators_and_provider_adapters() -> None:
    row = {"open": -1, "high": 0.5, "low": 2, "close": 0, "volume": -10}
    warnings = validate_ohlc(row)
    assert {
        "non_positive_price",
        "low_above_open_or_close",
        "negative_volume",
    } <= set(warnings)
    assert "high_below_open_or_close" in validate_ohlc(
        {"open": 5, "high": 3, "low": 2, "close": 4, "volume": 10}
    )
    assert NewsEngine().list_news("MSFT")
    news_profile = NewsProvider().get_company_profile("MSFT")
    assert news_profile is not None
    assert news_profile["ticker"] == "MSFT"
    assert DividendProvider().get_dividends("KO")
    assert MockProvider().get_daily_prices("MSFT")


def test_domain_models_and_value_objects() -> None:
    now = datetime.now(UTC)
    instrument = Instrument(
        ticker="MSFT",
        name="Microsoft",
        isin="DEMO",
        market="NASDAQ",
        exchange="NASDAQ",
        country="US",
        currency="USD",
        sector="Technology",
        industry="Software",
        provider="mock",
        data_quality_score=95,
        last_updated_at=now,
    )
    assert instrument.ticker == "MSFT"
    assert (
        DailyPrice(
            date=date.today(),
            ticker="MSFT",
            open=1,
            high=2,
            low=1,
            close=2,
            adjusted_close=2,
            volume=100,
            currency="USD",
            provider="mock",
            ingested_at=now,
            quality_score=90,
        ).close
        == 2
    )
    assert (
        Dividend(
            ticker="MSFT",
            ex_dividend_date=date.today(),
            payment_date=date.today(),
            amount=1,
            currency="USD",
            dividend_type="regular",
            provider="mock",
            ingested_at=now,
            quality_score=90,
        ).amount
        == 1
    )
    assert (
        NewsItem(
            id="1",
            headline="Demo",
            summary="Demo",
            source="Demo",
            url="https://example.com",
            published_at=now,
            tickers=["MSFT"],
            sentiment="neutral",
            confidence=0.8,
            provider="mock",
        ).sentiment
        == "neutral"
    )
    assert (
        PortfolioTransaction(
            id="1",
            portfolio_id="real",
            ticker="MSFT",
            transaction_type="buy",
            quantity=1,
            price=10,
            currency="USD",
            date=date.today(),
        ).transaction_type
        == "buy"
    )
    assert (
        Insight(
            id="1",
            ticker="MSFT",
            title="Signal",
            category="trend",
            severity="low",
            explanation="Demo",
            evidence={},
            confidence=0.8,
            generated_at=now,
            data_sources=["mock"],
        ).ticker
        == "MSFT"
    )
    assert (
        Forecast(
            ticker="MSFT",
            model_name="baseline",
            model_version="1",
            generated_at=now,
            horizon_days=30,
            scenario="central",
            expected_path=[],
            confidence_interval_low=1,
            confidence_interval_high=2,
            confidence=0.5,
            limitations=[],
        ).scenario
        == "central"
    )
    assert (
        Watchlist(
            id="1",
            name="List",
            description="Demo",
            items=[],
            created_at=now,
            updated_at=now,
        ).name
        == "List"
    )
    assert (
        DecisionJournalEntry(
            id="1",
            ticker="MSFT",
            decision_type="watch",
            thesis="Demo",
            risks=[],
            expected_horizon="5y",
            entry_price=10,
            snapshot_metrics={},
            status="active",
            review_date=date.today(),
            created_at=now,
            updated_at=now,
        ).status
        == "active"
    )
    assert (
        DataLineage(source="mock", as_of="today", confidence=0.8, data_kind=DataKind.MOCK).data_kind == "mock"
    )
    assert (
        MetricDescription(
            key="cagr",
            label="CAGR",
            meaning="Growth",
            calculation="formula",
            limitations="historical",
        ).key
        == "cagr"
    )
    assert Severity.HIGH == "high"
    assert TransactionType.BUY == "buy"


def test_repositories_and_forecast_request(tmp_path) -> None:
    status = demo_repository.ensure_demo_files(tmp_path)
    metadata = MetadataRepository(tmp_path / "data" / "longview.sqlite")
    metadata.set("check", "ok")
    assert metadata.get("check") == "ok"
    parquet = ParquetRepository(tmp_path / "data")
    assert parquet.aggregate_count() > 0
    assert parquet.read_prices("MSFT")
    portfolio_repo = PortfolioRepository()
    settings_repo = SettingsRepository()
    instrument_repo = InstrumentRepository()
    price_repo = PriceRepository()
    news_repo = NewsRepository()
    dividend_repo = DividendRepository()
    assert portfolio_repo.add({"ticker": "MSFT"})["ticker"] == "MSFT"
    assert settings_repo.all() == []
    assert instrument_repo.get("MSFT") is not None
    assert instrument_repo.search("micro")
    assert price_repo.get_daily_prices("MSFT")
    assert "MSFT" in price_repo.latest_prices(["MSFT", "UNKNOWN"])
    assert news_repo.list("MSFT")
    assert dividend_repo.list("KO")
    assert status["parquet"] == "ready"
    assert ForecastRequest(ticker="MSFT").horizon_days == 90
    assert SCENARIOS == ["adverse", "central", "optimistic"]
