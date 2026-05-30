from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.ingestion.provider_registry import ProviderRegistry
from app.ingestion.universe_loader import UniverseLoader
from app.repositories.ingestion_repository import IngestionRepository


class IngestionEngine:
    def __init__(self, db_path: Path, universe_root: Path) -> None:
        self.repository = IngestionRepository(db_path)
        self.universes = UniverseLoader(universe_root)
        self.providers = ProviderRegistry()

    def sync_ticker(self, ticker: str, provider_name: str = "yfinance") -> dict[str, Any]:
        provider = self.providers.get(provider_name)
        prices = provider.get_daily_prices(ticker)
        dividends = provider.get_dividends(ticker)
        return self.repository.create_job(
            {
                "id": f"ing_{uuid.uuid4().hex[:12]}",
                "type": "sync_ticker",
                "provider": provider_name,
                "ticker": ticker.upper(),
                "started_at": datetime.now(UTC).isoformat(),
                "finished_at": datetime.now(UTC).isoformat(),
                "status": "completed",
                "rows_prices": len(prices),
                "rows_dividends": len(dividends),
                "warnings": (
                    ["mock_fallback_used"] if prices and prices[0].get("data_kind") == "mock_fallback" else []
                ),
            }
        )

    def sync_universe(self, universe_id: str, provider_name: str = "yfinance") -> dict[str, Any]:
        universe = self.universes.load(universe_id)
        tickers = universe.get("tickers", [])
        rows_prices = 0
        rows_dividends = 0
        for ticker in tickers:
            job = self.sync_ticker(str(ticker), provider_name)
            rows_prices += int(job["rows_prices"])
            rows_dividends += int(job["rows_dividends"])
        return self.repository.create_job(
            {
                "id": f"ing_{uuid.uuid4().hex[:12]}",
                "type": "sync_universe",
                "provider": provider_name,
                "universe_id": universe_id,
                "started_at": datetime.now(UTC).isoformat(),
                "finished_at": datetime.now(UTC).isoformat(),
                "status": "completed",
                "rows_prices": rows_prices,
                "rows_dividends": rows_dividends,
            }
        )

    def daily_close(self) -> dict[str, Any]:
        return self.repository.create_job(
            {
                "id": f"ing_{uuid.uuid4().hex[:12]}",
                "type": "daily_close",
                "provider": "scheduler",
                "started_at": datetime.now(UTC).isoformat(),
                "finished_at": datetime.now(UTC).isoformat(),
                "status": "completed",
                "rows_prices": 0,
                "rows_dividends": 0,
                "rows_news": 0,
                "rows_fx": 8,
                "warnings": ["network_independent_dry_run"],
            }
        )
