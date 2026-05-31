from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.repositories.parquet_repository import ParquetRepository


class PriceRepository:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.parquet = ParquetRepository(data_dir or get_settings().data_dir)

    def get_daily_prices(self, ticker: str) -> list[dict[str, Any]]:
        return self.parquet.read_prices(ticker)

    def latest_prices(self, tickers: list[str]) -> dict[str, dict[str, Any]]:
        latest: dict[str, dict[str, Any]] = {}
        for ticker in tickers:
            rows = self.get_daily_prices(ticker)
            if rows:
                latest[ticker.upper()] = rows[-1]
        return latest
