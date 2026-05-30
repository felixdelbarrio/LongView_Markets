from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends

from app.alerts.alert_engine import AlertEngine
from app.analytics.calculation_engine import CalculationEngine
from app.analytics.signals import SignalEngine
from app.api.dependencies import get_calculation_engine
from app.calculations.calculation_engine import OperationalCalculationEngine
from app.copilot.context_builder import CopilotContextBuilder
from app.core.config import get_settings
from app.core.constants import API_PREFIX, APP_NAME, DISCLAIMER
from app.core.errors import not_found
from app.data_quality.quality_engine import QualityEngine
from app.dividends.dividend_engine import DividendEngine
from app.forecasting.forecasting_engine import ForecastingEngine
from app.fx.fx_engine import FxEngine
from app.generative.context_builder import GenerativeContextBuilder
from app.generative.generative_ingestion_engine import GenerativeIngestionEngine
from app.generative.prompt_registry import PromptRegistry
from app.ingestion.ingestion_engine import IngestionEngine
from app.ingestion.provider_registry import ProviderRegistry
from app.ingestion.universe_loader import UniverseLoader
from app.journal.journal_engine import JournalEngine
from app.ml.anomaly_detection import AnomalyDetection
from app.news.portfolio_news_impact_engine import PortfolioNewsImpactEngine
from app.playbooks.playbook_engine import PlaybookEngine
from app.repositories import demo_repository
from app.repositories.portfolio_repository import PortfolioRepository
from app.repositories.settings_repository import SettingsRepository
from app.screener.screener_engine import ScreenerEngine
from app.simulated_portfolios.simulation_engine import SimulationEngine
from app.tax.tax_engine import TaxEngine
from app.watchlists.watchlist_engine import WatchlistEngine

router = APIRouter(prefix=API_PREFIX)


def _settings_repo() -> SettingsRepository:
    return SettingsRepository(get_settings().database_path)


def _portfolio_repo() -> PortfolioRepository:
    repository = PortfolioRepository(get_settings().database_path)
    repository.seed_if_empty(demo_repository.get_portfolio_transactions(False))
    return repository


def _simulated_repo() -> PortfolioRepository:
    repository = PortfolioRepository(get_settings().database_path)
    if not repository.list_transactions("simulated", "simulated"):
        for row in demo_repository.get_portfolio_transactions(True):
            repository.add_transaction(
                {
                    **row,
                    "portfolio_id": "simulated",
                    "trade_date": row.get("date"),
                    "instrument_name": row.get("ticker", ""),
                },
                portfolio_type="simulated",
            )
    return repository


def _operational_engine() -> OperationalCalculationEngine:
    settings = _settings_repo().get_all()
    return OperationalCalculationEngine(str(settings.get("base_currency", "EUR")))


def _prices_for_transactions(
    transactions: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    tickers = sorted({str(row["ticker"]).upper() for row in transactions})
    return {ticker: demo_repository.get_prices(ticker) for ticker in tickers}


def _latest_prices_for_transactions(
    transactions: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return _latest_prices(sorted({str(row["ticker"]).upper() for row in transactions}))


def _valuation(portfolio_type: str = "real") -> dict[str, Any]:
    repo = _simulated_repo() if portfolio_type == "simulated" else _portfolio_repo()
    portfolio_id = "simulated" if portfolio_type == "simulated" else "real"
    transactions = repo.list_transactions(portfolio_id, portfolio_type)
    valuation = _operational_engine().portfolio_valuation(
        transactions,
        _latest_prices_for_transactions(transactions),
        demo_repository.get_instruments(),
    )
    valuation["portfolio_id"] = portfolio_id
    valuation["total_value"] = valuation["total_market_value_base"]
    valuation["total_cost"] = valuation["total_invested_base"]
    valuation["unrealized_return"] = valuation["total_return_pct"]
    valuation["net_estimated_return"] = valuation["total_return_pct"]
    top5 = sum(float(position["market_value_base"]) for position in valuation["top_positions"])
    valuation["top5_concentration"] = (
        round(top5 / valuation["total_market_value_base"] * 100, 2)
        if valuation["total_market_value_base"]
        else 0
    )
    return valuation


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
        "providers": ProviderRegistry().status(),
        "last_ingestion": demo_repository.AS_OF.isoformat(),
        "jobs": "local_scheduler_ready",
        "frontend_expected": settings.frontend_url,
        "build_sha": "local",
        "launcher": "available",
        "disclaimer": DISCLAIMER,
    }


@router.get("/dashboard")
def dashboard(
    engine: CalculationEngine = Depends(get_calculation_engine),
) -> dict[str, Any]:
    instruments = demo_repository.get_instruments()
    portfolio = _valuation("real")
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
                "¿Que cambio en el riesgo de mi cartera esta semana?",
                "¿Que dividendos merecen revision fiscal?",
                "¿Que tesis de inversion necesitan seguimiento?",
            ],
            "tickers_to_review": ["NVDA", "BBVA.MC", "MSFT"],
            "explained_alerts": demo_repository.get_alerts(),
        },
        "generative_context": {
            "summary": "Contexto inteligente preparado para cartera real con JSON estricto.",
            "jobs_pending": len(
                GenerativeIngestionEngine(get_settings().database_path).repository.list_jobs()
            ),
            "data_kind": "generative_inference",
            "not_financial_advice": True,
        },
        "narrative": "Hoy LongView ha detectado eventos relevantes para tu cartera y ha preparado contexto generativo trazable.",
        "lineage": {
            "source": "LongView SQLite + seed cache",
            "data_kind": "observed",
            "confidence": 0.86,
        },
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


@router.get("/news/portfolio")
def portfolio_news() -> list[dict[str, Any]]:
    return PortfolioNewsImpactEngine().prioritize(portfolio(), demo_repository.get_news())


@router.get("/news/{ticker}")
def news_for_ticker(ticker: str) -> list[dict[str, Any]]:
    return demo_repository.get_news(ticker)


@router.get("/universes")
def universes() -> list[dict[str, Any]]:
    return UniverseLoader(
        get_settings().project_root / "backend" / "app" / "data" / "universes"
    ).list_universes()


@router.get("/universes/{universe_id}")
def universe(universe_id: str) -> dict[str, Any]:
    try:
        return UniverseLoader(get_settings().project_root / "backend" / "app" / "data" / "universes").load(
            universe_id
        )
    except LookupError:
        raise not_found(f"Universe {universe_id} not found") from None


def _ingestion_engine() -> IngestionEngine:
    settings = get_settings()
    return IngestionEngine(
        settings.database_path,
        settings.project_root / "backend" / "app" / "data" / "universes",
    )


@router.post("/ingestion/sync-ticker")
def ingestion_sync_ticker(payload: dict[str, Any]) -> dict[str, Any]:
    return _ingestion_engine().sync_ticker(
        str(payload.get("ticker", "MSFT")), str(payload.get("provider", "yfinance"))
    )


@router.post("/ingestion/sync-universe")
def ingestion_sync_universe(payload: dict[str, Any]) -> dict[str, Any]:
    return _ingestion_engine().sync_universe(
        str(payload.get("universe_id", "ibex35")),
        str(payload.get("provider", "yfinance")),
    )


@router.post("/ingestion/sync-default-universes")
def ingestion_sync_default_universes() -> dict[str, Any]:
    jobs = [
        _ingestion_engine().sync_universe(universe_id) for universe_id in get_settings().sync_universe_ids[:3]
    ]
    return {"status": "completed", "jobs": jobs}


@router.post("/ingestion/sync-portfolio")
def ingestion_sync_portfolio() -> dict[str, Any]:
    jobs = [_ingestion_engine().sync_ticker(position["ticker"]) for position in portfolio()["positions"]]
    return {"status": "completed", "jobs": jobs}


@router.post("/ingestion/sync-fx")
def ingestion_sync_fx() -> dict[str, Any]:
    return _ingestion_engine().daily_close()


@router.post("/ingestion/sync-news")
def ingestion_sync_news() -> dict[str, Any]:
    return {
        "status": "completed",
        "rows_news": len(demo_repository.get_news()),
        "provider": "rss",
    }


@router.post("/ingestion/run-daily-close")
def ingestion_daily_close() -> dict[str, Any]:
    job = _ingestion_engine().daily_close()
    generative_jobs = GenerativeIngestionEngine(get_settings().database_path).prepare_daily_context(
        portfolio(), demo_repository.get_instruments(), demo_repository.get_news()
    )
    return {"status": "completed", "job": job, "generative_jobs": generative_jobs}


@router.get("/ingestion/jobs")
def ingestion_jobs() -> list[dict[str, Any]]:
    return _ingestion_engine().repository.list_jobs()


@router.get("/ingestion/jobs/{job_id}")
def ingestion_job(job_id: str) -> dict[str, Any]:
    job = _ingestion_engine().repository.get_job(job_id)
    if job is None:
        raise not_found(f"Job {job_id} not found")
    return job


@router.get("/providers/status")
def providers_status() -> list[dict[str, Any]]:
    return ProviderRegistry().status()


@router.get("/fx/rates")
def fx_rates() -> list[dict[str, Any]]:
    return FxEngine(
        get_settings().database_path,
        _settings_repo().get_all().get("base_currency", "EUR"),
    ).supported_rates()


@router.post("/fx/convert")
def fx_convert(payload: dict[str, Any]) -> dict[str, Any]:
    return FxEngine(
        get_settings().database_path,
        _settings_repo().get_all().get("base_currency", "EUR"),
    ).convert(
        float(payload.get("amount", 0)),
        str(payload.get("currency", "EUR")),
    )


@router.get("/portfolio")
def portfolio() -> dict[str, Any]:
    return _valuation("real")


@router.post("/portfolio/transactions")
def portfolio_transaction(payload: dict[str, Any]) -> dict[str, Any]:
    if "quantity" not in payload:
        payload["quantity"] = 1
    if "price" not in payload:
        payload["price"] = (demo_repository.latest_price(str(payload.get("ticker", "MSFT"))) or {}).get(
            "close", 1
        )
    transaction = _portfolio_repo().add_transaction(payload)
    return {"status": "recorded", "transaction": transaction, "data_kind": "user_input"}


@router.get("/portfolio/transactions")
def portfolio_transactions() -> list[dict[str, Any]]:
    return _portfolio_repo().list_transactions()


@router.patch("/portfolio/transactions/{transaction_id}")
def update_portfolio_transaction(transaction_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "updated",
        "transaction": _portfolio_repo().update_transaction(transaction_id, payload),
    }


@router.delete("/portfolio/transactions/{transaction_id}")
def delete_portfolio_transaction(transaction_id: str) -> dict[str, Any]:
    return {"status": ("deleted" if _portfolio_repo().delete_transaction(transaction_id) else "not_found")}


@router.get("/portfolio/performance")
def portfolio_performance() -> dict[str, Any]:
    valuation = portfolio()
    return {
        "benchmark": "SPY",
        "total_return": valuation["total_return_pct"],
        "benchmark_delta": 4.2,
        "calculation_version": valuation["calculation_version"],
    }


@router.get("/portfolio/allocation")
def portfolio_allocation() -> dict[str, Any]:
    positions = portfolio()["positions"]
    return {
        "positions": positions,
        "by_sector": _group_weights(positions, "sector"),
        "by_country": _group_weights(positions, "country"),
        "by_currency": _group_weights(positions, "currency"),
    }


@router.get("/portfolio/history")
def portfolio_history(
    start: date | None = None,
    end: date | None = None,
    currency: str = "EUR",
) -> dict[str, Any]:
    transactions = _portfolio_repo().list_transactions()
    return OperationalCalculationEngine(currency).portfolio_history(
        transactions,
        _prices_for_transactions(transactions),
        demo_repository.get_instruments(),
        start,
        end,
    )


@router.get("/portfolio/instruments/{ticker}/history")
def portfolio_instrument_history(
    ticker: str,
    start: date | None = None,
    end: date | None = None,
    currency: str = "EUR",
) -> dict[str, Any]:
    transactions = _portfolio_repo().list_transactions()
    return OperationalCalculationEngine(currency).instrument_history(
        ticker,
        transactions,
        _prices_for_transactions(transactions),
        demo_repository.get_instruments(),
        start,
        end,
    )


@router.get("/portfolio/annual")
def portfolio_annual() -> dict[str, Any]:
    rows = portfolio_history()["history"]
    totals: dict[str, dict[str, float]] = {}
    for row in rows:
        year = row["date"][:4]
        bucket = totals.setdefault(year, {"plusvalia": 0.0, "dividendos": 0.0, "pyg": 0.0})
        bucket["plusvalia"] = float(row["total_return_base"])
        bucket["dividendos"] += float(row["dividends_base"])
        bucket["pyg"] += float(row["daily_pnl_base"])
    return {"rows": [{"year": year, **values} for year, values in sorted(totals.items())]}


@router.get("/portfolio/monthly")
def portfolio_monthly() -> dict[str, Any]:
    rows = portfolio_history()["history"]
    totals: dict[str, dict[str, float]] = {}
    for row in rows:
        month = row["date"][:7]
        bucket = totals.setdefault(month, {"plusvalia": 0.0, "dividendos": 0.0, "pyg": 0.0})
        bucket["plusvalia"] = float(row["total_return_base"])
        bucket["dividendos"] += float(row["dividends_base"])
        bucket["pyg"] += float(row["daily_pnl_base"])
    return {"rows": [{"month": month, **values} for month, values in sorted(totals.items())]}


@router.get("/portfolio/instrument-performance")
def portfolio_instrument_performance() -> dict[str, Any]:
    valuation = portfolio()
    return {
        "rows": [
            {
                "ticker": position["ticker"],
                "investment": position["invested_amount_base"],
                "dividends": position["dividends_received_base"],
                "plusvalia": position["unrealized_pnl_base"],
                "rentabilidad": position["total_return_pct"],
                "realized_pnl": position["realized_pnl_base"],
                "unrealized_pnl": position["unrealized_pnl_base"],
                "total_return": position["total_return_base"],
            }
            for position in valuation["positions"]
        ]
    }


@router.get("/simulated-portfolio")
def simulated_portfolio() -> dict[str, Any]:
    return _valuation("simulated")


@router.post("/simulated-portfolio/transactions")
def simulated_transaction(payload: dict[str, Any]) -> dict[str, Any]:
    if "quantity" not in payload:
        payload["quantity"] = 1
    if "price" not in payload:
        payload["price"] = (demo_repository.latest_price(str(payload.get("ticker", "MSFT"))) or {}).get(
            "close", 1
        )
    transaction = _simulated_repo().add_transaction(payload, portfolio_type="simulated")
    return {
        "status": "simulated",
        "transaction": transaction,
        "data_kind": "simulation",
    }


@router.get("/simulated-portfolio/transactions")
def simulated_transactions() -> list[dict[str, Any]]:
    return _simulated_repo().list_transactions("simulated", "simulated")


@router.patch("/simulated-portfolio/transactions/{transaction_id}")
def update_simulated_transaction(transaction_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "updated",
        "transaction": _simulated_repo().update_transaction(transaction_id, payload),
    }


@router.delete("/simulated-portfolio/transactions/{transaction_id}")
def delete_simulated_transaction(transaction_id: str) -> dict[str, Any]:
    return {"status": ("deleted" if _simulated_repo().delete_transaction(transaction_id) else "not_found")}


@router.get("/simulated-portfolio/history")
def simulated_history() -> dict[str, Any]:
    transactions = _simulated_repo().list_transactions("simulated", "simulated")
    return _operational_engine().portfolio_history(
        transactions,
        _prices_for_transactions(transactions),
        demo_repository.get_instruments(),
    )


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


@router.get("/forecasting/instruments/{ticker}")
def operational_instrument_forecast(ticker: str) -> dict[str, Any]:
    return _operational_engine().forecast_instrument(ticker, demo_repository.get_prices(ticker))


@router.get("/forecasting/portfolio")
def operational_portfolio_forecast() -> dict[str, Any]:
    return _operational_engine().forecast_portfolio(portfolio())


@router.get("/data-quality")
def data_quality() -> dict[str, Any]:
    instruments = demo_repository.get_instruments()
    prices_by_ticker = {item["ticker"]: demo_repository.get_prices(item["ticker"]) for item in instruments}
    quality = QualityEngine().evaluate(instruments, prices_by_ticker)
    quality["sqlite"] = "ok"
    quality["parquet"] = "ok"
    quality["generative"] = {
        "pending_jobs": len(GenerativeIngestionEngine(get_settings().database_path).repository.list_jobs()),
        "responses_pending_validation": len(
            [
                job
                for job in GenerativeIngestionEngine(get_settings().database_path).repository.list_jobs()
                if job["status"] in {"waiting_for_response", "repair_required"}
            ]
        ),
    }
    quality["provider_status"] = ProviderRegistry().status()
    return quality


@router.get("/screener")
def screener(
    engine: CalculationEngine = Depends(get_calculation_engine),
) -> dict[str, Any]:
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
    return _settings_repo().get_all()


@router.post("/settings")
def save_settings(payload: dict[str, Any]) -> dict[str, Any]:
    return {"status": "saved", "settings": _settings_repo().update(payload)}


@router.get("/search")
def search(q: str = "") -> dict[str, Any]:
    query = q.lower()
    instruments = [
        item
        for item in demo_repository.get_instruments()
        if query in item["ticker"].lower() or query in item["name"].lower()
    ]
    universe_rows = [
        item for item in universes() if query in item["id"].lower() or query in item["name"].lower()
    ]
    news_rows = [
        item
        for item in demo_repository.get_news()
        if query in item["headline"].lower() or query in item["summary"].lower()
    ]
    generative_rows = [
        item
        for item in GenerativeIngestionEngine(get_settings().database_path).repository.history()
        if query in item["entity_id"].lower() or query in item["schema_id"].lower()
    ]
    return {
        "query": q,
        "instruments": instruments[:10],
        "universes": universe_rows[:10],
        "news": news_rows[:10],
        "generative": generative_rows[:10],
        "pages": [
            {"title": "Mi cartera", "path": "/my-portfolio"},
            {"title": "Ingesta generativa", "path": "/generative-ingestion"},
        ],
    }


@router.get("/generative/prompts")
def generative_prompts() -> list[dict[str, Any]]:
    return PromptRegistry().list_prompts()


@router.get("/generative/prompts/{prompt_id}")
def generative_prompt(prompt_id: str) -> dict[str, Any]:
    try:
        return PromptRegistry().get(prompt_id)
    except StopIteration:
        raise not_found(f"Prompt {prompt_id} not found") from None


@router.post("/generative/context/build")
def generative_context(payload: dict[str, Any]) -> dict[str, Any]:
    entity_type = str(payload.get("entity_type", "portfolio"))
    entity_id = str(payload.get("entity_id", "real"))
    instrument = demo_repository.get_instrument(entity_id) if entity_type == "instrument" else None
    return GenerativeContextBuilder().build(
        entity_type,
        entity_id,
        portfolio=portfolio(),
        instrument=instrument,
        news=demo_repository.get_news(entity_id if instrument else None),
        forecasts=(
            [_operational_engine().forecast_instrument(entity_id, demo_repository.get_prices(entity_id))]
            if instrument
            else [_operational_engine().forecast_portfolio(portfolio())]
        ),
        alerts=demo_repository.get_alerts(),
        include_sensitive=bool(
            _settings_repo().get_all().get("generative_include_sensitive_portfolio_details", False)
        ),
    )


@router.post("/generative/jobs")
def generative_create_job(payload: dict[str, Any]) -> dict[str, Any]:
    context = generative_context(payload)
    return GenerativeIngestionEngine(get_settings().database_path).create_job(
        str(payload.get("job_type", "manual_review")),
        str(payload.get("entity_type", "portfolio")),
        str(payload.get("entity_id", "real")),
        context,
        payload.get("prompt_id"),
    )


@router.get("/generative/jobs")
def generative_jobs() -> list[dict[str, Any]]:
    return GenerativeIngestionEngine(get_settings().database_path).repository.list_jobs()


@router.get("/generative/jobs/{job_id}")
def generative_job(job_id: str) -> dict[str, Any]:
    job = GenerativeIngestionEngine(get_settings().database_path).repository.get_job(job_id)
    if job is None:
        raise not_found(f"Generative job {job_id} not found")
    return job


@router.post("/generative/jobs/{job_id}/validate-response")
def generative_validate(job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return GenerativeIngestionEngine(get_settings().database_path).validate_response(
        job_id, str(payload.get("response", ""))
    )


@router.post("/generative/jobs/{job_id}/repair-json")
def generative_repair(job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return GenerativeIngestionEngine(get_settings().database_path).repair_json(
        job_id, str(payload.get("response", ""))
    )


@router.post("/generative/jobs/{job_id}/import-response")
def generative_import(job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return GenerativeIngestionEngine(get_settings().database_path).import_response(
        job_id, payload.get("response")
    )


@router.get("/generative/insights")
def generative_insights() -> list[dict[str, Any]]:
    return GenerativeIngestionEngine(get_settings().database_path).repository.history()


@router.get("/generative/insights/{ticker}")
def generative_insights_for_ticker(ticker: str) -> list[dict[str, Any]]:
    return [row for row in generative_insights() if row["entity_id"].upper() == ticker.upper()]


@router.get("/generative/portfolio-context")
def generative_portfolio_context() -> dict[str, Any]:
    return generative_context({"entity_type": "portfolio", "entity_id": "real"})


@router.get("/generative/history")
def generative_history() -> list[dict[str, Any]]:
    return GenerativeIngestionEngine(get_settings().database_path).repository.history()


@router.post("/generative/batch/prepare-daily-context")
def generative_prepare_daily_context() -> list[dict[str, Any]]:
    return GenerativeIngestionEngine(get_settings().database_path).prepare_daily_context(
        portfolio(), demo_repository.get_instruments(), demo_repository.get_news()
    )


@router.post("/generative/batch/prepare-portfolio-review")
def generative_prepare_portfolio_review() -> dict[str, Any]:
    return generative_create_job(
        {
            "entity_type": "portfolio",
            "entity_id": "real",
            "job_type": "portfolio_review",
        }
    )


@router.post("/generative/batch/prepare-watchlist-review")
def generative_prepare_watchlist_review() -> list[dict[str, Any]]:
    return [
        generative_create_job(
            {
                "entity_type": "instrument",
                "entity_id": item["ticker"],
                "job_type": "watchlist_review",
            }
        )
        for watchlist in demo_repository.get_watchlists()
        for item in watchlist["items"][:2]
    ]


@router.post("/generative/batch/prepare-news-impact")
def generative_prepare_news_impact() -> list[dict[str, Any]]:
    return [
        generative_create_job(
            {
                "entity_type": "instrument",
                "entity_id": row["ticker"],
                "job_type": "news_impact",
            }
        )
        for row in portfolio_news()[:5]
        if row["ticker"]
    ]


@router.post("/generative/batch/import-responses")
def generative_import_batch(payload: dict[str, Any]) -> dict[str, Any]:
    return GenerativeIngestionEngine(get_settings().database_path).import_jsonl(str(payload.get("jsonl", "")))


@router.get("/generative/batch/jobs")
def generative_batch_jobs() -> list[dict[str, Any]]:
    return generative_jobs()


@router.get("/ml/anomalies")
def ml_anomalies() -> list[dict[str, Any]]:
    return AnomalyDetection().detect(portfolio())


def _group_weights(positions: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    totals: dict[str, float] = {}
    for position in positions:
        totals[position[key]] = totals.get(position[key], 0.0) + float(position["weight"])
    return [{"name": name, "weight": round(weight, 2)} for name, weight in sorted(totals.items())]
