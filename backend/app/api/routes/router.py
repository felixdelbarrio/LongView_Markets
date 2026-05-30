from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.alerts.alert_engine import AlertEngine
from app.analytics.calculation_engine import CalculationEngine
from app.analytics.signals import SignalEngine
from app.api.dependencies import get_calculation_engine
from app.copilot.context_builder import CopilotContextBuilder
from app.core.config import get_settings
from app.core.constants import API_PREFIX, APP_NAME, DISCLAIMER
from app.core.errors import not_found
from app.data_quality.quality_engine import QualityEngine
from app.dividends.dividend_engine import DividendEngine
from app.forecasting.forecasting_engine import ForecastingEngine
from app.journal.journal_engine import JournalEngine
from app.playbooks.playbook_engine import PlaybookEngine
from app.portfolios.portfolio_engine import PortfolioEngine
from app.repositories import demo_repository
from app.screener.screener_engine import ScreenerEngine
from app.simulated_portfolios.simulation_engine import SimulationEngine
from app.tax.tax_engine import TaxEngine
from app.watchlists.watchlist_engine import WatchlistEngine

router = APIRouter(prefix=API_PREFIX)


def _analytics_for(ticker: str, engine: CalculationEngine) -> dict[str, Any]:
    prices = demo_repository.get_prices(ticker)
    if not prices:
        raise not_found(f"Ticker {ticker} not found")
    return engine.calculate_price_metrics(
        prices,
        demo_repository.get_prices("SPY"),
        demo_repository.get_dividends(ticker),
    )


def _latest_prices(tickers: list[str] | None = None) -> dict[str, dict[str, Any]]:
    symbols = tickers or [instrument["ticker"] for instrument in demo_repository.get_instruments()]
    prices: dict[str, dict[str, Any]] = {}
    for ticker in symbols:
        latest = demo_repository.latest_price(ticker)
        if latest is not None:
            prices[ticker] = latest
    return prices


@router.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    status = demo_repository.ensure_demo_files(settings.project_root)
    version_path = settings.project_root / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "0.1.0"
    return {
        "app": APP_NAME,
        "status": "ok",
        "version": version,
        "environment": settings.app_env,
        "parquet": status["parquet"],
        "sqlite": "ready",
        "providers": [{"name": "mock", "status": "ready", "confidence": 0.9}],
        "last_ingestion": demo_repository.AS_OF.isoformat(),
        "jobs": "local_scheduler_ready",
        "frontend_expected": settings.frontend_url,
        "build_sha": "local",
        "launcher": "available",
        "disclaimer": DISCLAIMER,
    }


@router.get("/dashboard")
def dashboard(engine: CalculationEngine = Depends(get_calculation_engine)) -> dict[str, Any]:
    instruments = demo_repository.get_instruments()
    portfolio = PortfolioEngine().summarize(
        demo_repository.get_portfolio_transactions(False),
        _latest_prices(),
        instruments,
    )
    analytics = {item["ticker"]: _analytics_for(item["ticker"], engine) for item in instruments[:12]}
    screener = ScreenerEngine().screen(instruments[:30], analytics)
    return {
        "hero": {
            "portfolio_value": portfolio["total_value"],
            "total_return": portfolio["unrealized_return"],
            "ytd_return": 9.8,
            "aggregate_risk": "medium",
            "upcoming_dividends": len(demo_repository.get_dividends()),
            "critical_alerts": 1,
            "data_status": "ready",
        },
        "market_pulse": demo_repository.get_markets(),
        "opportunities": screener[:8],
        "risk": portfolio,
        "discipline": {
            "journal_reviews": demo_repository.get_journal_entries(),
            "watchlists": demo_repository.get_watchlists(),
            "simulations": demo_repository.get_portfolio_transactions(True),
        },
        "copilot": {
            "questions": [
                "What changed in my portfolio risk this week?",
                "Which demo dividend events deserve tax review?",
                "Which watchlist entries need a thesis update?",
            ],
            "tickers_to_review": ["NVDA", "BBVA.MC", "MSFT"],
            "explained_alerts": demo_repository.get_alerts(),
        },
        "narrative": "Hoy LongView ha detectado 5 eventos relevantes para tu cartera.",
        "lineage": {"source": "LongView deterministic seed", "data_kind": "mock", "confidence": 0.86},
    }


@router.get("/markets")
def markets() -> list[dict[str, Any]]:
    return demo_repository.get_markets()


@router.get("/instruments")
def instruments() -> list[dict[str, Any]]:
    return demo_repository.get_instruments()


@router.get("/instruments/search")
def instrument_search(q: str = "") -> list[dict[str, Any]]:
    query = q.lower()
    return [
        item
        for item in demo_repository.get_instruments()
        if query in item["ticker"].lower() or query in item["name"].lower()
    ]


@router.get("/instruments/{ticker}")
def instrument_detail(
    ticker: str, engine: CalculationEngine = Depends(get_calculation_engine)
) -> dict[str, Any]:
    instrument = demo_repository.get_instrument(ticker)
    if instrument is None:
        raise not_found(f"Ticker {ticker} not found")
    analytics = _analytics_for(instrument["ticker"], engine)
    return {
        "instrument": instrument,
        "latest_price": demo_repository.latest_price(ticker),
        "prices": demo_repository.get_prices(ticker)[-260:],
        "analytics": analytics,
        "insights": SignalEngine().build_signals(instrument["ticker"], analytics),
        "news": demo_repository.get_news(ticker),
        "dividends": demo_repository.get_dividends(ticker),
        "forecast": ForecastingEngine().forecast(instrument["ticker"], demo_repository.get_prices(ticker)),
    }


@router.get("/prices/{ticker}")
def prices(ticker: str) -> list[dict[str, Any]]:
    rows = demo_repository.get_prices(ticker)
    if not rows:
        raise not_found(f"Ticker {ticker} not found")
    return rows


@router.post("/prices/sync")
def prices_sync() -> dict[str, Any]:
    return demo_repository.ensure_demo_files(get_settings().project_root)


@router.get("/analytics/{ticker}")
def analytics(ticker: str, engine: CalculationEngine = Depends(get_calculation_engine)) -> dict[str, Any]:
    return _analytics_for(ticker, engine)


@router.get("/insights/{ticker}")
def insights(
    ticker: str, engine: CalculationEngine = Depends(get_calculation_engine)
) -> list[dict[str, Any]]:
    return SignalEngine().build_signals(ticker, _analytics_for(ticker, engine))


@router.get("/signals/{ticker}")
def signals(ticker: str, engine: CalculationEngine = Depends(get_calculation_engine)) -> list[dict[str, Any]]:
    return SignalEngine().build_signals(ticker, _analytics_for(ticker, engine))


@router.get("/alerts")
def alerts() -> list[dict[str, Any]]:
    return AlertEngine().list_alerts()


@router.post("/alerts")
def create_alert(payload: dict[str, Any]) -> dict[str, Any]:
    return AlertEngine().create_alert(payload)


@router.patch("/alerts/{alert_id}")
def update_alert(alert_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"id": alert_id, "status": payload.get("status", "read"), "updated": True}


@router.get("/news")
def news() -> list[dict[str, Any]]:
    return demo_repository.get_news()


@router.get("/news/{ticker}")
def news_for_ticker(ticker: str) -> list[dict[str, Any]]:
    return demo_repository.get_news(ticker)


@router.get("/portfolio")
def portfolio() -> dict[str, Any]:
    instruments = demo_repository.get_instruments()
    return PortfolioEngine().summarize(
        demo_repository.get_portfolio_transactions(False), _latest_prices(), instruments
    )


@router.post("/portfolio/transactions")
def portfolio_transaction(payload: dict[str, Any]) -> dict[str, Any]:
    return {"status": "recorded", "transaction": payload, "data_kind": "user_input"}


@router.get("/portfolio/performance")
def portfolio_performance() -> dict[str, Any]:
    return {"benchmark": "SPY", "total_return": portfolio()["unrealized_return"], "benchmark_delta": 4.2}


@router.get("/portfolio/allocation")
def portfolio_allocation() -> dict[str, Any]:
    positions = portfolio()["positions"]
    return {
        "positions": positions,
        "by_sector": _group_weights(positions, "sector"),
        "by_country": _group_weights(positions, "country"),
        "by_currency": _group_weights(positions, "currency"),
    }


@router.get("/simulated-portfolio")
def simulated_portfolio() -> dict[str, Any]:
    return SimulationEngine().summarize(
        demo_repository.get_portfolio_transactions(True), _latest_prices(), demo_repository.get_instruments()
    )


@router.post("/simulated-portfolio/transactions")
def simulated_transaction(payload: dict[str, Any]) -> dict[str, Any]:
    return {"status": "simulated", "transaction": payload, "data_kind": "simulation"}


@router.get("/simulated-portfolio/performance")
def simulated_performance() -> dict[str, Any]:
    return {
        "total_return": simulated_portfolio()["unrealized_return"],
        "compare_to_real": portfolio()["unrealized_return"],
    }


@router.post("/simulated-portfolio/convert-to-real")
def convert_simulated(payload: dict[str, Any]) -> dict[str, Any]:
    return SimulationEngine().convert_to_real(payload)


@router.get("/dividends")
def dividends() -> list[dict[str, Any]]:
    return demo_repository.get_dividends()


@router.get("/dividends/calendar")
def dividend_calendar() -> list[dict[str, Any]]:
    return DividendEngine().calendar(demo_repository.get_dividends())


@router.get("/dividends/opportunities")
def dividend_opportunities() -> list[dict[str, Any]]:
    return DividendEngine().opportunities(demo_repository.get_dividends(), _latest_prices())


@router.get("/tax/rules")
def tax_rules(country: str | None = None) -> list[dict[str, Any]]:
    return TaxEngine().load_rules(country)


@router.post("/tax/estimate")
def tax_estimate(payload: dict[str, Any]) -> dict[str, Any]:
    return TaxEngine().estimate(payload)


@router.get("/forecasting/{ticker}")
def forecasting(ticker: str) -> dict[str, Any]:
    rows = demo_repository.get_prices(ticker)
    if not rows:
        raise not_found(f"Ticker {ticker} not found")
    return ForecastingEngine().forecast(ticker, rows)


@router.get("/data-quality")
def data_quality() -> dict[str, Any]:
    instruments = demo_repository.get_instruments()
    prices_by_ticker = {item["ticker"]: demo_repository.get_prices(item["ticker"]) for item in instruments}
    return QualityEngine().evaluate(instruments, prices_by_ticker)


@router.get("/screener")
def screener(engine: CalculationEngine = Depends(get_calculation_engine)) -> dict[str, Any]:
    instruments = demo_repository.get_instruments()
    analytics_by_ticker = {item["ticker"]: _analytics_for(item["ticker"], engine) for item in instruments}
    return {
        "presets": ScreenerEngine.presets,
        "results": ScreenerEngine().screen(instruments, analytics_by_ticker),
    }


@router.post("/screener/presets")
def create_screener_preset(payload: dict[str, Any]) -> dict[str, Any]:
    return {"status": "saved", "preset": payload}


@router.get("/watchlists")
def watchlists() -> list[dict[str, Any]]:
    return WatchlistEngine().list_watchlists()


@router.post("/watchlists")
def create_watchlist(payload: dict[str, Any]) -> dict[str, Any]:
    return WatchlistEngine().create(payload)


@router.post("/watchlists/{watchlist_id}/items")
def add_watchlist_item(watchlist_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"watchlist_id": watchlist_id, "item": payload, "status": "added"}


@router.get("/journal")
def journal() -> list[dict[str, Any]]:
    return JournalEngine().list_entries()


@router.post("/journal")
def create_journal(payload: dict[str, Any]) -> dict[str, Any]:
    return JournalEngine().create(payload)


@router.patch("/journal/{entry_id}")
def update_journal(entry_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"id": entry_id, "status": payload.get("status", "updated"), "updated": True}


@router.get("/playbooks")
def playbooks() -> list[dict[str, Any]]:
    return PlaybookEngine().list_playbooks()


@router.get("/copilot/context/{ticker}")
def copilot_context(
    ticker: str, engine: CalculationEngine = Depends(get_calculation_engine)
) -> dict[str, Any]:
    instrument = demo_repository.get_instrument(ticker)
    if instrument is None:
        raise not_found(f"Ticker {ticker} not found")
    return CopilotContextBuilder().build(
        ticker,
        instrument,
        _analytics_for(ticker, engine),
        demo_repository.get_news(ticker),
        demo_repository.get_settings(),
    )


@router.get("/settings")
def settings() -> dict[str, Any]:
    return demo_repository.get_settings()


@router.post("/settings")
def save_settings(payload: dict[str, Any]) -> dict[str, Any]:
    return {"status": "saved", "settings": {**demo_repository.get_settings(), **payload}}


def _group_weights(positions: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    totals: dict[str, float] = {}
    for position in positions:
        totals[position[key]] = totals.get(position[key], 0.0) + float(position["weight"])
    return [{"name": name, "weight": round(weight, 2)} for name, weight in sorted(totals.items())]
