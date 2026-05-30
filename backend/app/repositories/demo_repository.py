from __future__ import annotations

import json
import math
import sqlite3
from datetime import UTC, date, datetime, timedelta
from functools import cache
from pathlib import Path
from typing import Any

from app.core.constants import DEMO_PROVIDER

AS_OF = datetime(2026, 5, 29, 18, 0, tzinfo=UTC)
PRICE_START = date(2023, 5, 30)
PRICE_END = date(2026, 5, 29)

INSTRUMENT_SPECS: list[dict[str, str]] = [
    {
        "ticker": "AAPL",
        "name": "Apple",
        "market": "NASDAQ",
        "exchange": "NASDAQ",
        "country": "US",
        "currency": "USD",
        "sector": "Technology",
        "industry": "Consumer electronics",
    },
    {
        "ticker": "MSFT",
        "name": "Microsoft",
        "market": "NASDAQ",
        "exchange": "NASDAQ",
        "country": "US",
        "currency": "USD",
        "sector": "Technology",
        "industry": "Software",
    },
    {
        "ticker": "NVDA",
        "name": "Nvidia",
        "market": "NASDAQ",
        "exchange": "NASDAQ",
        "country": "US",
        "currency": "USD",
        "sector": "Technology",
        "industry": "Semiconductors",
    },
    {
        "ticker": "GOOGL",
        "name": "Alphabet",
        "market": "NASDAQ",
        "exchange": "NASDAQ",
        "country": "US",
        "currency": "USD",
        "sector": "Communication Services",
        "industry": "Internet",
    },
    {
        "ticker": "AMZN",
        "name": "Amazon",
        "market": "NASDAQ",
        "exchange": "NASDAQ",
        "country": "US",
        "currency": "USD",
        "sector": "Consumer Discretionary",
        "industry": "E-commerce",
    },
    {
        "ticker": "META",
        "name": "Meta",
        "market": "NASDAQ",
        "exchange": "NASDAQ",
        "country": "US",
        "currency": "USD",
        "sector": "Communication Services",
        "industry": "Social platforms",
    },
    {
        "ticker": "TSLA",
        "name": "Tesla",
        "market": "NASDAQ",
        "exchange": "NASDAQ",
        "country": "US",
        "currency": "USD",
        "sector": "Consumer Discretionary",
        "industry": "Automobiles",
    },
    {
        "ticker": "BRK.B",
        "name": "Berkshire Hathaway",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "US",
        "currency": "USD",
        "sector": "Financials",
        "industry": "Holding company",
    },
    {
        "ticker": "JPM",
        "name": "JPMorgan",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "US",
        "currency": "USD",
        "sector": "Financials",
        "industry": "Banking",
    },
    {
        "ticker": "KO",
        "name": "Coca-Cola",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "US",
        "currency": "USD",
        "sector": "Consumer Staples",
        "industry": "Beverages",
    },
    {
        "ticker": "JNJ",
        "name": "Johnson & Johnson",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "US",
        "currency": "USD",
        "sector": "Health Care",
        "industry": "Pharmaceuticals",
    },
    {
        "ticker": "PG",
        "name": "Procter & Gamble",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "US",
        "currency": "USD",
        "sector": "Consumer Staples",
        "industry": "Household products",
    },
    {
        "ticker": "BBVA.MC",
        "name": "BBVA",
        "market": "BME",
        "exchange": "BME",
        "country": "ES",
        "currency": "EUR",
        "sector": "Financials",
        "industry": "Banking",
    },
    {
        "ticker": "SAN.MC",
        "name": "Santander",
        "market": "BME",
        "exchange": "BME",
        "country": "ES",
        "currency": "EUR",
        "sector": "Financials",
        "industry": "Banking",
    },
    {
        "ticker": "ITX.MC",
        "name": "Inditex",
        "market": "BME",
        "exchange": "BME",
        "country": "ES",
        "currency": "EUR",
        "sector": "Consumer Discretionary",
        "industry": "Retail",
    },
    {
        "ticker": "IBE.MC",
        "name": "Iberdrola",
        "market": "BME",
        "exchange": "BME",
        "country": "ES",
        "currency": "EUR",
        "sector": "Utilities",
        "industry": "Electric utilities",
    },
    {
        "ticker": "REP.MC",
        "name": "Repsol",
        "market": "BME",
        "exchange": "BME",
        "country": "ES",
        "currency": "EUR",
        "sector": "Energy",
        "industry": "Integrated energy",
    },
    {
        "ticker": "ASML.AS",
        "name": "ASML",
        "market": "Euronext",
        "exchange": "Amsterdam",
        "country": "NL",
        "currency": "EUR",
        "sector": "Technology",
        "industry": "Semiconductor equipment",
    },
    {
        "ticker": "MC.PA",
        "name": "LVMH",
        "market": "Euronext",
        "exchange": "Paris",
        "country": "FR",
        "currency": "EUR",
        "sector": "Consumer Discretionary",
        "industry": "Luxury goods",
    },
    {
        "ticker": "NESN.SW",
        "name": "Nestle",
        "market": "SIX",
        "exchange": "SIX",
        "country": "CH",
        "currency": "CHF",
        "sector": "Consumer Staples",
        "industry": "Food",
    },
    {
        "ticker": "ROG.SW",
        "name": "Roche",
        "market": "SIX",
        "exchange": "SIX",
        "country": "CH",
        "currency": "CHF",
        "sector": "Health Care",
        "industry": "Pharmaceuticals",
    },
    {
        "ticker": "TM",
        "name": "Toyota",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "JP",
        "currency": "USD",
        "sector": "Consumer Discretionary",
        "industry": "Automobiles",
    },
    {
        "ticker": "NVO",
        "name": "Novo Nordisk",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "DK",
        "currency": "USD",
        "sector": "Health Care",
        "industry": "Biotechnology",
    },
    {
        "ticker": "SAP.DE",
        "name": "SAP",
        "market": "XETRA",
        "exchange": "XETRA",
        "country": "DE",
        "currency": "EUR",
        "sector": "Technology",
        "industry": "Enterprise software",
    },
    {
        "ticker": "ALV.DE",
        "name": "Allianz",
        "market": "XETRA",
        "exchange": "XETRA",
        "country": "DE",
        "currency": "EUR",
        "sector": "Financials",
        "industry": "Insurance",
    },
    {
        "ticker": "UL",
        "name": "Unilever",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "GB",
        "currency": "USD",
        "sector": "Consumer Staples",
        "industry": "Personal products",
    },
    {
        "ticker": "TSM",
        "name": "TSMC",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "TW",
        "currency": "USD",
        "sector": "Technology",
        "industry": "Semiconductors",
    },
    {
        "ticker": "SONY",
        "name": "Sony",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "JP",
        "currency": "USD",
        "sector": "Consumer Discretionary",
        "industry": "Electronics",
    },
    {
        "ticker": "MELI",
        "name": "MercadoLibre",
        "market": "NASDAQ",
        "exchange": "NASDAQ",
        "country": "UY",
        "currency": "USD",
        "sector": "Consumer Discretionary",
        "industry": "E-commerce",
    },
    {
        "ticker": "SHOP",
        "name": "Shopify",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "CA",
        "currency": "USD",
        "sector": "Technology",
        "industry": "Commerce software",
    },
    {
        "ticker": "SPY",
        "name": "S&P 500 ETF benchmark",
        "market": "NYSE",
        "exchange": "NYSE",
        "country": "US",
        "currency": "USD",
        "sector": "Benchmark",
        "industry": "ETF",
    },
]


def stable_number(value: str) -> int:
    return sum((index + 1) * ord(char) for index, char in enumerate(value))


def business_days(start: date = PRICE_START, end: date = PRICE_END) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


@cache
def get_instruments() -> list[dict[str, Any]]:
    instruments: list[dict[str, Any]] = []
    for spec in INSTRUMENT_SPECS:
        quality = 88 + stable_number(spec["ticker"]) % 12
        instruments.append(
            {
                **spec,
                "isin": f"DEMO{stable_number(spec['ticker']):08d}",
                "provider": DEMO_PROVIDER,
                "data_quality_score": quality,
                "last_updated_at": AS_OF.isoformat(),
                "data_kind": "mock",
                "source": "LongView deterministic seed",
                "confidence": round(quality / 100, 2),
            }
        )
    return instruments


def get_instrument(ticker: str) -> dict[str, Any] | None:
    normalized = ticker.upper()
    return next(
        (item for item in get_instruments() if item["ticker"].upper() == normalized),
        None,
    )


@cache
def get_prices(ticker: str) -> list[dict[str, Any]]:
    instrument = get_instrument(ticker)
    if instrument is None:
        return []
    seed = stable_number(instrument["ticker"])
    base = 35 + seed % 260
    yearly_growth = 0.015 + (seed % 14) / 100
    volatility = 0.010 + (seed % 9) / 1000
    rows: list[dict[str, Any]] = []
    previous = float(base)
    for index, current_date in enumerate(business_days()):
        years = index / 252
        regime = math.sin(index / 37 + seed / 11) * volatility
        cycle = math.sin(index / 91 + seed / 17) * 0.018
        shock = -0.16 * math.exp(-(((index - 285) / 42) ** 2)) if seed % 5 == 0 else 0
        drift = yearly_growth / 252
        close = max(1.5, previous * (1 + drift + regime + cycle / 252 + shock / 252))
        if index % 63 == 0 and index > 0:
            close *= 1 + ((seed % 7) - 3) / 100
        open_price = previous * (1 + math.sin(index + seed) * 0.004)
        high = max(open_price, close) * (1 + 0.006 + (seed % 5) / 2000)
        low = min(open_price, close) * (1 - 0.006 - (seed % 3) / 2000)
        volume = int(800_000 + (seed % 2_400_000) + abs(math.sin(index / 13)) * 1_600_000)
        rows.append(
            {
                "date": current_date.isoformat(),
                "ticker": instrument["ticker"],
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "adjusted_close": round(close * (1 + 0.004 * years), 2),
                "volume": volume,
                "currency": instrument["currency"],
                "provider": DEMO_PROVIDER,
                "ingested_at": AS_OF.isoformat(),
                "quality_score": instrument["data_quality_score"],
                "source": "LongView deterministic seed",
                "confidence": round(instrument["data_quality_score"] / 100, 2),
                "data_kind": "mock",
            }
        )
        previous = close
    return rows


def latest_price(ticker: str) -> dict[str, Any] | None:
    prices = get_prices(ticker)
    return prices[-1] if prices else None


def require_latest_price(ticker: str) -> dict[str, Any]:
    price = latest_price(ticker)
    if price is None:
        raise LookupError(f"Missing latest price for {ticker}")
    return price


def get_dividends(ticker: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for instrument in get_instruments():
        seed = stable_number(instrument["ticker"])
        if instrument["sector"] in {"Technology", "Benchmark"} and seed % 3 == 0:
            continue
        amount = round(0.16 + (seed % 90) / 100, 2)
        for quarter in range(4):
            ex_date = date(2026, 6 + quarter * 2 if quarter < 3 else 12, 8 + seed % 12)
            rows.append(
                {
                    "ticker": instrument["ticker"],
                    "ex_dividend_date": ex_date.isoformat(),
                    "payment_date": (ex_date + timedelta(days=21)).isoformat(),
                    "amount": amount,
                    "currency": instrument["currency"],
                    "dividend_type": "regular",
                    "provider": DEMO_PROVIDER,
                    "ingested_at": AS_OF.isoformat(),
                    "quality_score": instrument["data_quality_score"],
                    "source": "LongView deterministic seed",
                    "confidence": round(instrument["data_quality_score"] / 100, 2),
                    "data_kind": "mock",
                }
            )
    if ticker:
        return [row for row in rows if row["ticker"].upper() == ticker.upper()]
    return rows


def get_news(ticker: str | None = None) -> list[dict[str, Any]]:
    news: list[dict[str, Any]] = []
    topics = [
        (
            "capital discipline",
            "improves cash generation while management keeps long-term guidance prudent",
            "positive",
        ),
        (
            "margin pressure",
            "faces higher input costs and currency headwinds in the next two quarters",
            "negative",
        ),
        (
            "dividend calendar",
            "confirms a regular dividend event with moderate estimated yield",
            "neutral",
        ),
        (
            "data quality watch",
            "has one provider with stale volume data and should be reviewed before acting",
            "neutral",
        ),
    ]
    for index, instrument in enumerate(get_instruments()[:30]):
        topic, summary, sentiment = topics[index % len(topics)]
        news.append(
            {
                "id": f"news-{instrument['ticker'].replace('.', '-')}-{index}",
                "headline": f"{instrument['name']} {topic} update",
                "summary": f"Demo news: {instrument['name']} {summary}. This is mock context for long-term review.",
                "source": "LongView Demo Wire",
                "url": "https://example.com/longview-demo-news",
                "published_at": (AS_OF - timedelta(hours=index * 3)).isoformat(),
                "tickers": [instrument["ticker"]],
                "sentiment": sentiment,
                "confidence": 0.71 + (index % 20) / 100,
                "provider": DEMO_PROVIDER,
                "data_kind": "mock",
            }
        )
    if ticker:
        return [item for item in news if ticker.upper() in [symbol.upper() for symbol in item["tickers"]]]
    return news


def get_portfolio_transactions(simulated: bool = False) -> list[dict[str, Any]]:
    tickers = (
        ["MSFT", "NVDA", "BBVA.MC", "KO", "ASML.AS", "IBE.MC"]
        if not simulated
        else ["NVO", "MC.PA", "TSM", "ALV.DE", "SHOP"]
    )
    rows: list[dict[str, Any]] = []
    for index, ticker in enumerate(tickers):
        prices = get_prices(ticker)
        instrument = get_instrument(ticker)
        buy_price = prices[80 + index * 35]["close"]
        quantity = 8 + index * 3
        rows.append(
            {
                "id": f"{'sim' if simulated else 'real'}-buy-{index}",
                "portfolio_id": "simulated" if simulated else "real",
                "ticker": ticker,
                "transaction_type": "buy",
                "quantity": quantity,
                "price": buy_price,
                "currency": instrument["currency"] if instrument else "USD",
                "fees": round(1.5 + index * 0.7, 2),
                "taxes": 0,
                "date": prices[80 + index * 35]["date"],
                "notes": "Demo position created by LongView seed data.",
            }
        )
    return rows


def get_alerts() -> list[dict[str, Any]]:
    return [
        {
            "id": "alert-nvda-volatility",
            "title": "Nvidia shows high recent volatility",
            "severity": "high",
            "category": "risk",
            "ticker": "NVDA",
            "explanation": "The 30-day volatility is above its demo universe percentile.",
            "evidence": {"metric": "volatility_annualized", "threshold": 0.32},
            "source": "calculation_engine",
            "generated_at": AS_OF.isoformat(),
            "confidence": 0.83,
            "status": "new",
            "data_kind": "mock",
            "suggested_action": "Review position sizing and thesis before adding exposure.",
        },
        {
            "id": "alert-bbva-dividend",
            "title": "BBVA has an upcoming ex-dividend event",
            "severity": "medium",
            "category": "dividend",
            "ticker": "BBVA.MC",
            "explanation": "A regular dividend event is scheduled in the deterministic demo calendar.",
            "evidence": {"days_to_ex_dividend": 17},
            "source": "dividend_engine",
            "generated_at": AS_OF.isoformat(),
            "confidence": 0.78,
            "status": "new",
            "data_kind": "mock",
            "suggested_action": "Model tax, spread and price-adjustment risk before acting.",
        },
    ]


def get_watchlists() -> list[dict[str, Any]]:
    now = AS_OF.isoformat()
    return [
        {
            "id": "dividends",
            "name": "Dividendos",
            "description": "Stable dividend candidates to review",
            "items": [
                {"ticker": "KO", "reason": "regularity"},
                {"ticker": "BBVA.MC", "reason": "upcoming dividend"},
            ],
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "quality-tech",
            "name": "Tecnologia calidad",
            "description": "Large compounders with strong data coverage",
            "items": [
                {"ticker": "MSFT", "reason": "quality"},
                {"ticker": "ASML.AS", "reason": "moat"},
            ],
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "europe-defensive",
            "name": "Europa defensiva",
            "description": "Lower-volatility European exposures",
            "items": [
                {"ticker": "IBE.MC", "reason": "utilities"},
                {"ticker": "ALV.DE", "reason": "income"},
            ],
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "drawdown",
            "name": "Oportunidades en drawdown",
            "description": "Quality assets with relevant drawdown",
            "items": [
                {"ticker": "SHOP", "reason": "drawdown"},
                {"ticker": "MELI", "reason": "watch volatility"},
            ],
            "created_at": now,
            "updated_at": now,
        },
    ]


def get_journal_entries() -> list[dict[str, Any]]:
    now = AS_OF.isoformat()
    return [
        {
            "id": "journal-msft-quality",
            "ticker": "MSFT",
            "decision_type": "watch",
            "thesis": "Compounder review: durable cash generation, high valuation discipline required.",
            "risks": ["valuation compression", "AI capex execution", "currency"],
            "expected_horizon": "5 years",
            "entry_price": require_latest_price("MSFT")["close"],
            "snapshot_metrics": {"confidence": 0.86, "trend": "uptrend"},
            "status": "active",
            "review_date": "2026-11-30",
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "journal-bbva-dividend",
            "ticker": "BBVA.MC",
            "decision_type": "simulate",
            "thesis": "Dividend capture only makes sense if tax and spread remain controlled.",
            "risks": [
                "ex-dividend price adjustment",
                "withholding tax",
                "bank cyclicality",
            ],
            "expected_horizon": "90 days",
            "entry_price": require_latest_price("BBVA.MC")["close"],
            "snapshot_metrics": {"confidence": 0.74, "dividend_yield": 0.045},
            "status": "needs_review",
            "review_date": "2026-07-15",
            "created_at": now,
            "updated_at": now,
        },
    ]


def get_playbooks() -> list[dict[str, Any]]:
    names = [
        "Long-term investing",
        "Dividend capture",
        "DCA contributions",
        "Portfolio rebalancing",
        "Concentration management",
        "How to interpret drawdown",
        "Reading forecasts prudently",
        "Using a simulated portfolio",
    ]
    return [
        {
            "id": name.lower().replace(" ", "-"),
            "title": name,
            "use_case": "Use when evaluating disciplined long-term decisions.",
            "risks": ["overconfidence", "data gaps", "tax assumptions"],
            "metrics": ["CAGR", "drawdown", "volatility", "confidence"],
            "how_to_use": "Open the relevant app section, inspect evidence, and document a thesis before acting.",
            "warning": "This is educational guidance, not financial advice.",
        }
        for name in names
    ]


def get_settings() -> dict[str, Any]:
    return {
        "theme": "system",
        "language": "es",
        "fiscal_country": "ES",
        "base_currency": "EUR",
        "data_provider": "mock",
        "external_gpt_url": "https://chatgpt.com/g/g-longview-markets",
        "context_depth": "balanced",
        "risk_profile": "balanced",
        "update_frequency": "daily",
        "alerts_enabled": True,
        "data_kind": "mock",
    }


def get_markets() -> list[dict[str, Any]]:
    markets: dict[str, dict[str, Any]] = {}
    for instrument in get_instruments():
        prices = get_prices(instrument["ticker"])
        if not prices:
            continue
        previous = prices[-2]["close"]
        current = prices[-1]["close"]
        market = markets.setdefault(
            instrument["market"],
            {
                "market": instrument["market"],
                "change": 0.0,
                "members": 0,
                "leaders": [],
                "source": DEMO_PROVIDER,
                "data_kind": "mock",
            },
        )
        market["change"] += (current - previous) / previous
        market["members"] += 1
        market["leaders"].append(
            {
                "ticker": instrument["ticker"],
                "change": round((current - previous) / previous * 100, 2),
            }
        )
    for market in markets.values():
        market["change"] = round(market["change"] / max(market["members"], 1) * 100, 2)
        market["leaders"] = sorted(market["leaders"], key=lambda item: item["change"], reverse=True)[:3]
    return list(markets.values())


def seed_snapshot() -> dict[str, Any]:
    return {
        "generated_at": AS_OF.isoformat(),
        "provider": DEMO_PROVIDER,
        "instruments": get_instruments(),
        "portfolio": get_portfolio_transactions(False),
        "simulated_portfolio": get_portfolio_transactions(True),
        "alerts": get_alerts(),
        "watchlists": get_watchlists(),
        "journal": get_journal_entries(),
        "settings": get_settings(),
    }


def ensure_sqlite(data_dir: Path) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "longview.sqlite"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value, updated_at) VALUES (?, ?, ?)",
            ("seed_provider", DEMO_PROVIDER, AS_OF.isoformat()),
        )
        connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value, updated_at) VALUES (?, ?, ?)",
            ("app_version", "0.1.0", AS_OF.isoformat()),
        )
    return db_path


def ensure_demo_files(project_root: Path) -> dict[str, Any]:
    data_dir = project_root / "data"
    (data_dir / "seed").mkdir(parents=True, exist_ok=True)
    (data_dir / "raw").mkdir(parents=True, exist_ok=True)
    (data_dir / "curated").mkdir(parents=True, exist_ok=True)
    seed_path = data_dir / "seed" / "longview_seed.json"
    seed_path.write_text(json.dumps(seed_snapshot(), indent=2, ensure_ascii=False), encoding="utf-8")
    sqlite_path = ensure_sqlite(data_dir)
    parquet_status = "ready"
    try:
        import polars as pl

        for instrument in get_instruments():
            ticker = instrument["ticker"]
            for year in {row["date"][:4] for row in get_prices(ticker)}:
                rows = [row for row in get_prices(ticker) if row["date"].startswith(year)]
                target = (
                    data_dir
                    / "parquet"
                    / "prices"
                    / f"market={instrument['market']}"
                    / f"ticker={ticker}"
                    / f"year={year}"
                )
                target.mkdir(parents=True, exist_ok=True)
                pl.DataFrame(rows).write_parquet(target / "prices.parquet")
            dividend_rows = get_dividends(ticker)
            if dividend_rows:
                target = (
                    data_dir
                    / "parquet"
                    / "dividends"
                    / f"market={instrument['market']}"
                    / f"ticker={ticker}"
                    / "year=2026"
                )
                target.mkdir(parents=True, exist_ok=True)
                pl.DataFrame(dividend_rows).write_parquet(target / "dividends.parquet")
        news_target = data_dir / "parquet" / "news" / "year=2026"
        news_target.mkdir(parents=True, exist_ok=True)
        pl.DataFrame(get_news()).write_parquet(news_target / "news.parquet")
        for relative in [
            "fx",
            "portfolio_snapshots/portfolio_id=real/year=2026",
            "instrument_position_snapshots/portfolio_id=real/ticker=MSFT/year=2026",
            "forecasts",
            "signals",
            "features/entity=portfolio",
            "features/entity=instrument",
            "generative/entity=portfolio/year=2026",
            "generative/entity=instrument/ticker=MSFT/year=2026",
        ]:
            target = data_dir / "parquet" / relative
            target.mkdir(parents=True, exist_ok=True)
            marker = target / "_READY.json"
            marker.write_text(
                json.dumps({"status": "ready", "generated_at": AS_OF.isoformat()}),
                encoding="utf-8",
            )
    except Exception as exc:  # pragma: no cover - exercised only when optional parquet stack is missing.
        parquet_status = f"degraded: {exc}"
    return {
        "seed": str(seed_path),
        "sqlite": str(sqlite_path),
        "parquet": parquet_status,
    }
