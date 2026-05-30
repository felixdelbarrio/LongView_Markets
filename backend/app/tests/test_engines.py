from __future__ import annotations

from pathlib import Path

from app.alerts.alert_engine import AlertEngine
from app.analytics.calculation_engine import CalculationEngine
from app.data_quality.quality_engine import QualityEngine
from app.dividends.dividend_engine import DividendEngine
from app.forecasting.backtesting import simple_directional_accuracy
from app.forecasting.forecasting_engine import ForecastingEngine
from app.journal.journal_engine import JournalEngine
from app.providers.mock_provider import MockProvider
from app.repositories import demo_repository
from app.screener.screener_engine import ScreenerEngine
from app.simulated_portfolios.simulation_engine import SimulationEngine
from app.tax.tax_engine import TaxEngine
from app.watchlists.watchlist_engine import WatchlistEngine


def test_calculation_engine_metrics() -> None:
    prices = demo_repository.get_prices("MSFT")
    result = CalculationEngine().calculate_price_metrics(
        prices, demo_repository.get_prices("SPY"), demo_repository.get_dividends("MSFT")
    )
    assert result["status"] == "ok"
    assert result["metrics"]["current_price"] > 0
    assert "cagr" in result["descriptions"]


def test_portfolio_and_simulation_engines() -> None:
    latest = {
        item["ticker"]: demo_repository.require_latest_price(item["ticker"])
        for item in demo_repository.get_instruments()
    }
    summary = SimulationEngine().summarize(
        demo_repository.get_portfolio_transactions(True), latest, demo_repository.get_instruments()
    )
    assert summary["total_value"] > 0
    assert SimulationEngine().convert_to_real({"ticker": "MSFT"})["requires_confirmation"] is True


def test_dividend_tax_forecast_alert_quality_screener() -> None:
    latest = {
        item["ticker"]: demo_repository.require_latest_price(item["ticker"])
        for item in demo_repository.get_instruments()
    }
    opportunities = DividendEngine().opportunities(demo_repository.get_dividends(), latest)
    assert opportunities
    assert "disclaimer" in TaxEngine().estimate(
        {"residence_country": "ES", "dividends": 100, "capital_gains": 50}
    )
    forecast = ForecastingEngine().forecast("MSFT", demo_repository.get_prices("MSFT"))
    assert forecast["status"] == "ok"
    assert ForecastingEngine().detect_regime(demo_repository.get_prices("MSFT")) in {
        "recovery",
        "deterioration",
        "stable",
    }
    assert simple_directional_accuracy([1, 2, 3], [1, 1.5, 2]) == 1.0
    assert AlertEngine().create_alert({"title": "Test"})["status"] == "new"
    instruments = demo_repository.get_instruments()
    quality = QualityEngine().evaluate(
        instruments[:2],
        {item["ticker"]: demo_repository.get_prices(item["ticker"]) for item in instruments[:2]},
    )
    assert quality["global_score"] > 80
    analytics = {"MSFT": CalculationEngine().calculate_price_metrics(demo_repository.get_prices("MSFT"))}
    msft = demo_repository.get_instrument("MSFT")
    assert msft is not None
    assert ScreenerEngine().screen([msft], analytics)[0]["ticker"] == "MSFT"


def test_watchlist_journal_provider_and_seed(tmp_path: Path) -> None:
    assert WatchlistEngine().list_watchlists()
    assert JournalEngine().create({"ticker": "MSFT"})["ticker"] == "MSFT"
    provider = MockProvider()
    assert provider.search_instruments("apple")
    profile = provider.get_company_profile("AAPL")
    assert profile is not None
    assert profile["ticker"] == "AAPL"
    status = demo_repository.ensure_demo_files(tmp_path)
    assert Path(status["seed"]).exists()
    assert Path(status["sqlite"]).exists()
