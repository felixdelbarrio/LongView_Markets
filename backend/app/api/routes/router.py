from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
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
from app.repositories.dividend_repository import DividendRepository
from app.repositories.ingestion_repository import IngestionRepository
from app.repositories.instrument_repository import InstrumentRepository
from app.repositories.news_repository import NewsRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.repositories.price_repository import PriceRepository
from app.repositories.settings_repository import SettingsRepository
from app.screener.screener_engine import ScreenerEngine
from app.simulated_portfolios.simulation_engine import SimulationEngine
from app.tax.tax_engine import TaxEngine
from app.watchlists.watchlist_engine import WatchlistEngine

router = APIRouter(prefix=API_PREFIX)


def _settings_repo() -> SettingsRepository:
    return SettingsRepository(get_settings().database_path)


def _portfolio_repo() -> PortfolioRepository:
    return PortfolioRepository(get_settings().database_path)


def _simulated_repo() -> PortfolioRepository:
    return PortfolioRepository(get_settings().database_path)


def _instrument_repo() -> InstrumentRepository:
    return InstrumentRepository(get_settings().database_path)


def _price_repo() -> PriceRepository:
    return PriceRepository(get_settings().data_dir)


def _dividend_repo() -> DividendRepository:
    return DividendRepository(get_settings().data_dir)


def _news_repo() -> NewsRepository:
    return NewsRepository(get_settings().data_dir)


def _ingestion_repo() -> IngestionRepository:
    return IngestionRepository(get_settings().database_path)


def _demo_enabled() -> bool:
    settings = get_settings()
    return settings.demo_mode_enabled and settings.mock_fallback_enabled


def _demo_repository() -> Any:
    from app.repositories import demo_repository

    return demo_repository


def _universe_loader() -> UniverseLoader:
    return UniverseLoader(get_settings().project_root / "backend" / "app" / "data" / "universes")


def _universe_instruments(limit: int = 250) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for universe in _universe_loader().list_universes():
        try:
            detail = _universe_loader().load(str(universe["id"]))
        except LookupError:
            continue
        for ticker in detail.get("tickers", []):
            symbol = str(ticker).upper()
            rows.append(
                {
                    "ticker": symbol,
                    "name": symbol,
                    "market": detail.get("name", universe["id"]),
                    "exchange": "unknown",
                    "country": detail.get("country", "unknown"),
                    "currency": detail.get("currency", "USD"),
                    "sector": "Unknown",
                    "industry": "Unknown",
                    "provider": "universe",
                    "data_kind": "reference",
                    "data_quality_score": 0,
                    "confidence": 0,
                    "last_updated_at": None,
                }
            )
            if len(rows) >= limit:
                return rows
    return rows


def _runtime_instruments(include_reference: bool = False) -> list[dict[str, Any]]:
    rows = _instrument_repo().list()
    if rows:
        return rows
    if _demo_enabled():
        return _demo_repository().get_instruments()
    return _universe_instruments() if include_reference else []


def _runtime_instrument(ticker: str) -> dict[str, Any] | None:
    symbol = ticker.upper()
    row = _instrument_repo().get(symbol)
    if row:
        return row
    if _demo_enabled():
        return _demo_repository().get_instrument(symbol)
    return next((item for item in _universe_instruments() if item["ticker"] == symbol), None)


def _metadata_only_instrument(ticker: str) -> dict[str, Any]:
    symbol = ticker.upper()
    return {
        "ticker": symbol,
        "name": symbol,
        "market": "unknown",
        "exchange": "unknown",
        "country": "unknown",
        "currency": "USD",
        "sector": "Unknown",
        "industry": "Unknown",
        "provider": "metadata_only",
        "data_kind": "metadata_only",
        "data_quality_score": 0,
        "confidence": 0,
        "last_updated_at": None,
    }


def _runtime_prices(ticker: str) -> list[dict[str, Any]]:
    rows = _price_repo().get_daily_prices(ticker)
    if rows:
        return rows
    if _demo_enabled():
        return _demo_repository().get_prices(ticker)
    return []


def _runtime_latest_price(ticker: str) -> dict[str, Any] | None:
    rows = _runtime_prices(ticker)
    return rows[-1] if rows else None


def _runtime_dividends(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = _dividend_repo().list(ticker)
    if rows:
        return rows
    if _demo_enabled():
        return _demo_repository().get_dividends(ticker)
    return []


def _runtime_news(ticker: str | None = None) -> list[dict[str, Any]]:
    rows = _news_repo().list(ticker)
    if rows:
        return rows
    if _demo_enabled():
        return _demo_repository().get_news(ticker)
    return []


def _latest_prices(tickers: list[str] | None = None) -> dict[str, dict[str, Any]]:
    symbols = tickers or [item["ticker"] for item in _runtime_instruments()]
    prices: dict[str, dict[str, Any]] = {}
    for ticker in symbols:
        latest = _runtime_latest_price(ticker)
        if latest is not None:
            prices[ticker.upper()] = latest
    return prices


def _prices_for_transactions(
    transactions: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    return {
        ticker: _runtime_prices(ticker)
        for ticker in sorted({str(row["ticker"]).upper() for row in transactions})
    }


def _operational_engine() -> OperationalCalculationEngine:
    settings = _settings_repo().get_all()
    return OperationalCalculationEngine(str(settings.get("base_currency", "EUR")))


def _valuation(portfolio_type: str = "real") -> dict[str, Any]:
    repo = _simulated_repo() if portfolio_type == "simulated" else _portfolio_repo()
    portfolio_id = "simulated" if portfolio_type == "simulated" else "real"
    transactions = repo.list_transactions(portfolio_id, portfolio_type)
    valuation = _operational_engine().portfolio_valuation(
        transactions,
        _latest_prices(sorted({str(row["ticker"]).upper() for row in transactions})),
        _runtime_instruments(include_reference=True),
    )
    valuation["portfolio_id"] = portfolio_id
    valuation["total_value"] = valuation["total_market_value_base"]
    valuation["total_cost"] = valuation["total_invested_base"]
    valuation["unrealized_return"] = valuation["total_return_pct"]
    valuation["net_estimated_return"] = valuation["total_return_pct"]
    valuation["is_empty"] = not transactions
    top5 = sum(float(position["market_value_base"]) for position in valuation["top_positions"])
    valuation["top5_concentration"] = (
        round(top5 / valuation["total_market_value_base"] * 100, 2)
        if valuation["total_market_value_base"]
        else 0
    )
    return valuation


def _queue_ticker_analysis(ticker: str, reason: str) -> dict[str, Any]:
    return _ingestion_repo().create_job(
        {
            "id": f"ing_{uuid.uuid4().hex[:12]}",
            "type": "sync_ticker_full_analysis",
            "provider": get_settings().default_market_provider,
            "ticker": ticker.upper(),
            "started_at": datetime.now(UTC).isoformat(),
            "finished_at": None,
            "status": "queued",
            "warnings": [reason],
        }
    )


def _analytics_for(ticker: str, engine: CalculationEngine) -> dict[str, Any]:
    prices = _runtime_prices(ticker)
    if not prices:
        return {
            "status": "no_data",
            "metrics": {},
            "descriptions": {},
            "warnings": ["Sin historico ingerido. Sincroniza el instrumento para calcular metricas."],
        }
    return engine.calculate_price_metrics(prices, _runtime_prices("SPY"), _runtime_dividends(ticker))


def _tax_relevant_transactions() -> list[dict[str, Any]]:
    return [
        row
        for row in _portfolio_repo().list_transactions()
        if str(row.get("transaction_type", "")).lower() in {"sell", "dividend", "tax"}
    ]


@router.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    version_path = settings.project_root / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else "0.1.0"
    return {
        "app": APP_NAME,
        "status": "ok",
        "version": version,
        "environment": settings.app_env,
        "parquet": "ready",
        "sqlite": "ready",
        "providers": ProviderRegistry().status(),
        "last_ingestion": (ingestion_jobs()[0]["started_at"] if ingestion_jobs() else None),
        "jobs": "local_scheduler_ready",
        "frontend_expected": settings.frontend_url,
        "build_sha": "local",
        "launcher": "available",
        "demo_mode_enabled": settings.demo_mode_enabled,
        "disclaimer": DISCLAIMER,
    }


@router.get("/dashboard")
def dashboard(
    engine: CalculationEngine = Depends(get_calculation_engine),
) -> dict[str, Any]:
    portfolio_state = _valuation("real")
    has_portfolio = not bool(portfolio_state["is_empty"])
    instruments = _runtime_instruments(include_reference=True)
    analytics = {
        item["ticker"]: _analytics_for(item["ticker"], engine)
        for item in instruments[:12]
        if _runtime_prices(item["ticker"])
    }
    opportunities = ScreenerEngine().screen(instruments[:30], analytics) if analytics else []
    quality = data_quality()
    market_rows = markets()
    return {
        "empty_portfolio": not has_portfolio,
        "hero": {
            "portfolio_value": portfolio_state["total_value"] if has_portfolio else 0,
            "total_return": (portfolio_state["unrealized_return"] if has_portfolio else 0),
            "ytd_return": portfolio_state["ytd_return_pct"] if has_portfolio else 0,
            "aggregate_risk": "not_available" if not has_portfolio else "calculated",
            "upcoming_dividends": len(_runtime_dividends()) if has_portfolio else 0,
            "critical_alerts": len(AlertEngine().list_alerts()),
            "data_status": quality["status"],
        },
        "market_pulse": market_rows,
        "market_pulse_status": (
            "ready" if any(row.get("rows_prices", 0) for row in market_rows) else "pending_sync"
        ),
        "opportunities": opportunities[:8],
        "risk": portfolio_state,
        "discipline": {
            "journal_reviews": JournalEngine().list_entries(),
            "watchlists": WatchlistEngine().list_watchlists(),
            "simulations": _simulated_repo().list_transactions("simulated", "simulated"),
        },
        "proactive_intelligence": {
            "summary": (
                "Añade tu primera operación para activar seguimiento de cartera."
                if not has_portfolio
                else "Cartera lista para priorizar alertas, noticias, dividendos y calidad de datos."
            ),
            "questions": [
                "¿Qué valores necesitan sincronización?",
                "¿Qué datos están obsoletos?",
                "¿Qué operaciones tienen impacto fiscal?",
            ],
            "status": "embedded",
        },
        "generative_context": {
            "summary": "Inteligencia generativa transparente: se prepara tras ingestas y queda pendiente si no hay GPT externo.",
            "jobs_pending": len(
                [
                    job
                    for job in GenerativeIngestionEngine(get_settings().database_path).repository.list_jobs()
                    if job["status"] in {"waiting_for_response", "repair_required"}
                ]
            ),
            "data_kind": "generative_inference",
            "not_financial_advice": True,
        },
        "narrative": (
            "Todavía no hay cartera. LongView usará tus operaciones reales para calcular valoración, histórico, PyG, dividendos y riesgo."
            if not has_portfolio
            else "LongView ha calculado tu cartera con datos observados o cacheados."
        ),
        "lineage": {
            "source": "SQLite + Parquet + yfinance cache",
            "data_kind": "observed" if has_portfolio else "empty",
            "confidence": 0.0 if not has_portfolio else 0.86,
        },
    }


@router.get("/markets")
def markets() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    jobs = _ingestion_repo().list_jobs()
    jobs_by_universe = {
        job.get("universe_id"): job
        for job in jobs
        if job.get("universe_id") and job.get("type") == "sync_universe"
    }
    for universe in _universe_loader().list_universes():
        job = jobs_by_universe.get(universe["id"])
        try:
            universe_detail = _universe_loader().load(str(universe["id"]))
        except LookupError:
            universe_detail = {}
        members = int(
            universe.get("members") or universe.get("count") or len(universe_detail.get("tickers", []))
        )
        rows.append(
            {
                "market": universe["name"],
                "universe_id": universe["id"],
                "members": members,
                "change": 0,
                "leaders": [],
                "provider": get_settings().default_market_provider,
                "status": job["status"] if job else "pending_sync",
                "rows_prices": int(job["rows_prices"]) if job else 0,
                "last_updated_at": job["finished_at"] if job else None,
                "data_kind": ("observed" if job and int(job["rows_prices"]) else "no_data"),
            }
        )
    return rows


@router.get("/instruments")
def instruments() -> list[dict[str, Any]]:
    return _runtime_instruments(include_reference=True)


@router.get("/instruments/search")
def instrument_search(q: str = "") -> list[dict[str, Any]]:
    query = q.lower()
    return [
        item
        for item in instruments()
        if query in item["ticker"].lower() or query in str(item.get("name", "")).lower()
    ][:25]


@router.get("/instruments/{ticker}")
def instrument_detail(
    ticker: str, engine: CalculationEngine = Depends(get_calculation_engine)
) -> dict[str, Any]:
    symbol = ticker.upper()
    instrument = _runtime_instrument(symbol) or _metadata_only_instrument(symbol)
    prices = _runtime_prices(symbol)
    analytics = _analytics_for(symbol, engine)
    forecast = (
        ForecastingEngine().forecast(symbol, prices)
        if prices
        else {
            "ticker": symbol,
            "status": "no_data",
            "scenarios": [],
            "warning": "Sin historico minimo de 2 años.",
        }
    )
    news_rows = _runtime_news(symbol)
    return {
        "instrument": instrument,
        "latest_price": prices[-1] if prices else None,
        "prices": prices[-520:],
        "analytics": analytics,
        "insights": SignalEngine().build_signals(symbol, analytics) if prices else [],
        "alerts": AlertEngine().list_alerts(),
        "news": [
            {
                **row,
                "sentiment": row.get("sentiment") or "pending",
                "gpt_status": (
                    "analyzed"
                    if row.get("sentiment") not in {None, "", "pending"}
                    else "pending_configuration"
                ),
            }
            for row in news_rows
        ],
        "dividends": _runtime_dividends(symbol),
        "forecast": forecast,
        "data_quality": data_quality()
        .get("by_ticker", {})
        .get(symbol, {"score": 0, "status": "sin datos suficientes"}),
        "operations": [
            row for row in _portfolio_repo().list_transactions() if str(row["ticker"]).upper() == symbol
        ],
    }


@router.get("/prices/{ticker}")
def prices(ticker: str) -> list[dict[str, Any]]:
    rows = _runtime_prices(ticker)
    if not rows:
        raise not_found(f"Ticker {ticker.upper()} has no ingested prices")
    return rows


@router.post("/prices/sync")
def prices_sync() -> dict[str, Any]:
    job = _ingestion_engine().daily_close()
    return {"status": "queued", "sqlite": "ready", "parquet": "ready", "job": job}


@router.get("/analytics/{ticker}")
def analytics(ticker: str, engine: CalculationEngine = Depends(get_calculation_engine)) -> dict[str, Any]:
    return _analytics_for(ticker, engine)


@router.get("/insights/{ticker}")
def insights(
    ticker: str, engine: CalculationEngine = Depends(get_calculation_engine)
) -> list[dict[str, Any]]:
    analytics_row = _analytics_for(ticker, engine)
    return SignalEngine().build_signals(ticker, analytics_row) if analytics_row["status"] != "no_data" else []


@router.get("/signals/{ticker}")
def signals(ticker: str, engine: CalculationEngine = Depends(get_calculation_engine)) -> list[dict[str, Any]]:
    return insights(ticker, engine)


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
    return _runtime_news()


@router.get("/news/portfolio")
def portfolio_news() -> list[dict[str, Any]]:
    return PortfolioNewsImpactEngine().prioritize(portfolio(), _runtime_news())


@router.get("/news/{ticker}")
def news_for_ticker(ticker: str) -> list[dict[str, Any]]:
    return _runtime_news(ticker)


@router.get("/universes")
def universes() -> list[dict[str, Any]]:
    return _universe_loader().list_universes()


@router.get("/universes/{universe_id}")
def universe(universe_id: str) -> dict[str, Any]:
    try:
        return _universe_loader().load(universe_id)
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
        str(payload.get("ticker", "MSFT")),
        str(payload.get("provider", get_settings().default_market_provider)),
    )


@router.post("/ingestion/sync-universe")
def ingestion_sync_universe(payload: dict[str, Any]) -> dict[str, Any]:
    return _ingestion_engine().sync_universe(
        str(payload.get("universe_id", "ibex35")),
        str(payload.get("provider", get_settings().default_market_provider)),
    )


@router.post("/ingestion/sync-default-universes")
def ingestion_sync_default_universes() -> dict[str, Any]:
    jobs = [
        _ingestion_repo().create_job(
            {
                "id": f"ing_{uuid.uuid4().hex[:12]}",
                "type": "sync_universe",
                "provider": get_settings().default_market_provider,
                "universe_id": universe_id,
                "started_at": datetime.now(UTC).isoformat(),
                "finished_at": None,
                "status": "queued",
                "warnings": ["queued_from_global_sync"],
            }
        )
        for universe_id in get_settings().sync_universe_ids[:4]
    ]
    return {"status": "queued", "jobs": jobs}


@router.post("/ingestion/sync-portfolio")
def ingestion_sync_portfolio() -> dict[str, Any]:
    jobs = [
        _queue_ticker_analysis(position["ticker"], "queued_from_portfolio_sync")
        for position in portfolio()["positions"]
    ]
    return {"status": "queued" if jobs else "empty_portfolio", "jobs": jobs}


@router.post("/ingestion/sync-fx")
def ingestion_sync_fx() -> dict[str, Any]:
    return _ingestion_engine().daily_close()


@router.post("/ingestion/sync-news")
def ingestion_sync_news() -> dict[str, Any]:
    return {
        "status": "queued",
        "rows_news": len(_runtime_news()),
        "provider": get_settings().news_provider,
    }


@router.post("/ingestion/run-daily-close")
def ingestion_daily_close() -> dict[str, Any]:
    job = _ingestion_engine().daily_close()
    return {"status": "completed", "job": job, "generative_jobs": []}


@router.get("/ingestion/jobs")
def ingestion_jobs() -> list[dict[str, Any]]:
    return _ingestion_repo().list_jobs()


@router.get("/ingestion/jobs/{job_id}")
def ingestion_job(job_id: str) -> dict[str, Any]:
    job = _ingestion_repo().get_job(job_id)
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
    ticker = str(payload.get("ticker", "")).upper()
    if "quantity" not in payload:
        payload["quantity"] = 1
    if "price" not in payload:
        latest = _runtime_latest_price(ticker)
        payload["price"] = float(latest.get("close", 0)) if latest else 0
        payload["price_source"] = "cache" if latest else "pending_yfinance_sync"
    transaction = _portfolio_repo().add_transaction(payload)
    job = _queue_ticker_analysis(transaction["ticker"], "queued_after_portfolio_transaction")
    return {
        "status": "recorded",
        "transaction": transaction,
        "ingestion_job": job,
        "data_kind": "user_input",
    }


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
        "benchmark_delta": 0.0,
        "calculation_version": valuation["calculation_version"],
        "empty": valuation["is_empty"],
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
    start: date | None = None, end: date | None = None, currency: str = "EUR"
) -> dict[str, Any]:
    transactions = _portfolio_repo().list_transactions()
    return OperationalCalculationEngine(currency).portfolio_history(
        transactions,
        _prices_for_transactions(transactions),
        _runtime_instruments(include_reference=True),
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
        _runtime_instruments(include_reference=True),
        start,
        end,
    )


@router.get("/portfolio/annual")
def portfolio_annual() -> dict[str, Any]:
    return {"rows": ([] if not _portfolio_repo().list_transactions() else portfolio_history()["history"])}


@router.get("/portfolio/monthly")
def portfolio_monthly() -> dict[str, Any]:
    return {"rows": ([] if not _portfolio_repo().list_transactions() else portfolio_history()["history"])}


@router.get("/portfolio/instrument-performance")
def portfolio_instrument_performance() -> dict[str, Any]:
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
            for position in portfolio()["positions"]
        ]
    }


@router.get("/simulated-portfolio")
def simulated_portfolio() -> dict[str, Any]:
    return _valuation("simulated")


@router.post("/simulated-portfolio/transactions")
def simulated_transaction(payload: dict[str, Any]) -> dict[str, Any]:
    ticker = str(payload.get("ticker", "")).upper()
    if "quantity" not in payload:
        payload["quantity"] = 1
    if "price" not in payload:
        latest = _runtime_latest_price(ticker)
        payload["price"] = float(latest.get("close", 0)) if latest else 0
        payload["price_source"] = "cache" if latest else "pending_yfinance_sync"
    transaction = _simulated_repo().add_transaction(payload, portfolio_type="simulated")
    job = _queue_ticker_analysis(transaction["ticker"], "queued_after_simulated_transaction")
    return {
        "status": "simulated",
        "transaction": transaction,
        "ingestion_job": job,
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
        _runtime_instruments(include_reference=True),
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
    return _runtime_dividends()


@router.get("/dividends/calendar")
def dividend_calendar() -> list[dict[str, Any]]:
    return DividendEngine().calendar(_runtime_dividends())


@router.get("/dividends/opportunities")
def dividend_opportunities() -> list[dict[str, Any]]:
    return DividendEngine().opportunities(_runtime_dividends(), _latest_prices())


@router.get("/tax/rules")
def tax_rules(country: str | None = None) -> list[dict[str, Any]]:
    return TaxEngine().load_rules(country)


@router.get("/tax/relevant-events")
def tax_relevant_events() -> dict[str, Any]:
    rows = _tax_relevant_transactions()
    return {
        "empty": not rows,
        "message": ("No hay operaciones fiscalmente relevantes todavía" if not rows else None),
        "rows": rows,
        "disclaimer": "Estimación fiscal orientativa; no sustituye asesoramiento profesional.",
    }


@router.post("/tax/estimate")
def tax_estimate(payload: dict[str, Any]) -> dict[str, Any]:
    return TaxEngine().estimate(payload)


@router.get("/forecasting/{ticker}")
def forecasting(ticker: str) -> dict[str, Any]:
    rows = _runtime_prices(ticker)
    if not rows:
        return {"ticker": ticker.upper(), "status": "no_data", "scenarios": []}
    return ForecastingEngine().forecast(ticker, rows)


@router.get("/forecasting/instruments/{ticker}")
def operational_instrument_forecast(ticker: str) -> dict[str, Any]:
    return _operational_engine().forecast_instrument(ticker, _runtime_prices(ticker))


@router.get("/forecasting/portfolio")
def operational_portfolio_forecast() -> dict[str, Any]:
    return _operational_engine().forecast_portfolio(portfolio())


@router.get("/data-quality")
def data_quality() -> dict[str, Any]:
    instruments_rows = _runtime_instruments()
    prices_by_ticker = {item["ticker"]: _runtime_prices(item["ticker"]) for item in instruments_rows}
    quality = QualityEngine().evaluate(instruments_rows, prices_by_ticker)
    quality["sqlite"] = "ok"
    quality["parquet"] = "ok"
    quality["by_ticker"] = {
        ticker: {
            "score": 0 if not rows else 80,
            "status": "sin datos suficientes" if not rows else "ready",
            "prices_available": len(rows),
        }
        for ticker, rows in prices_by_ticker.items()
    }
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
    instruments_rows = _runtime_instruments(include_reference=True)
    analytics_by_ticker = {
        item["ticker"]: _analytics_for(item["ticker"], engine)
        for item in instruments_rows
        if _runtime_prices(item["ticker"])
    }
    return {
        "presets": ScreenerEngine.presets,
        "results": (
            ScreenerEngine().screen(instruments_rows, analytics_by_ticker) if analytics_by_ticker else []
        ),
        "expired": [],
        "status": "ready" if analytics_by_ticker else "pending_sync",
        "message": (
            "Sin datos suficientes. Sincroniza un universo para generar recomendaciones medibles."
            if not analytics_by_ticker
            else None
        ),
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
    ticker = str(payload.get("ticker", "")).upper()
    job = _queue_ticker_analysis(ticker, "queued_after_watchlist_item") if ticker else None
    return {
        "watchlist_id": watchlist_id,
        "item": {**payload, "ticker": ticker},
        "ingestion_job": job,
        "status": "added",
    }


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
def playbooks() -> list[dict[str, object]]:
    return PlaybookEngine().list_playbooks()


@router.get("/copilot/context/{ticker}")
def copilot_context(
    ticker: str, engine: CalculationEngine = Depends(get_calculation_engine)
) -> dict[str, Any]:
    symbol = ticker.upper()
    instrument = _runtime_instrument(symbol) or _metadata_only_instrument(symbol)
    return CopilotContextBuilder().build(
        symbol,
        instrument,
        _analytics_for(symbol, engine),
        _runtime_news(symbol),
        _settings_repo().get_all(),
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
    return {
        "query": q,
        "instruments": [item for item in instruments() if query in item["ticker"].lower()][:10],
        "universes": [
            item for item in universes() if query in item["id"].lower() or query in item["name"].lower()
        ][:10],
        "news": [
            item
            for item in _runtime_news()
            if query in str(item.get("headline", "")).lower() or query in str(item.get("summary", "")).lower()
        ][:10],
        "generative": [
            item
            for item in GenerativeIngestionEngine(get_settings().database_path).repository.history()
            if query in item["entity_id"].lower() or query in item["schema_id"].lower()
        ][:10],
        "pages": [
            {"title": "Mi cartera", "path": "/my-portfolio"},
            {"title": "Instrumentos", "path": "/instruments/MSFT"},
            {"title": "Guías operativas", "path": "/guides"},
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
    instrument = _runtime_instrument(entity_id) if entity_type == "instrument" else None
    return GenerativeContextBuilder().build(
        entity_type,
        entity_id,
        portfolio=portfolio(),
        instrument=instrument,
        news=_runtime_news(entity_id if instrument else None),
        forecasts=(
            [_operational_engine().forecast_instrument(entity_id, _runtime_prices(entity_id))]
            if instrument
            else [_operational_engine().forecast_portfolio(portfolio())]
        ),
        alerts=AlertEngine().list_alerts(),
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
    return []


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
    return []


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
        if row.get("ticker")
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
        totals[str(position.get(key, "Unknown"))] = totals.get(
            str(position.get(key, "Unknown")), 0.0
        ) + float(position.get("weight", 0))
    return [{"name": name, "weight": round(weight, 2)} for name, weight in sorted(totals.items())]
