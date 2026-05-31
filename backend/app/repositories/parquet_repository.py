from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb
import polars as pl


class ParquetRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def write_prices(self, ticker: str, rows: list[dict[str, Any]], provider: str) -> None:
        if not rows:
            return
        path = (
            self.data_dir
            / "parquet"
            / "prices"
            / f"provider={provider}"
            / f"ticker={ticker.upper()}"
            / "granularity=1d"
            / "prices.parquet"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        pl.DataFrame(rows).write_parquet(path)

    def read_prices(self, ticker: str) -> list[dict[str, Any]]:
        pattern = str(
            self.data_dir / "parquet" / "prices" / "*" / f"ticker={ticker.upper()}" / "*" / "prices.parquet"
        )
        try:
            rows = pl.scan_parquet(pattern).collect().sort("date").to_dicts()
            return rows
        except Exception:
            return []

    def write_dividends(self, ticker: str, rows: list[dict[str, Any]], provider: str) -> None:
        if not rows:
            return
        path = (
            self.data_dir
            / "parquet"
            / "dividends"
            / f"provider={provider}"
            / f"ticker={ticker.upper()}"
            / "dividends.parquet"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        pl.DataFrame(rows).write_parquet(path)

    def read_dividends(self, ticker: str | None = None) -> list[dict[str, Any]]:
        ticker_part = f"ticker={ticker.upper()}" if ticker else "ticker=*"
        pattern = str(self.data_dir / "parquet" / "dividends" / "*" / ticker_part / "dividends.parquet")
        try:
            return pl.scan_parquet(pattern).collect().sort("ex_dividend_date").to_dicts()
        except Exception:
            return []

    def write_news(self, ticker: str, rows: list[dict[str, Any]], provider: str) -> None:
        if not rows:
            return
        path = (
            self.data_dir
            / "parquet"
            / "news"
            / f"provider={provider}"
            / f"ticker={ticker.upper()}"
            / "news.parquet"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        pl.DataFrame(rows).write_parquet(path)

    def read_news(self, ticker: str | None = None) -> list[dict[str, Any]]:
        ticker_part = f"ticker={ticker.upper()}" if ticker else "ticker=*"
        pattern = str(self.data_dir / "parquet" / "news" / "*" / ticker_part / "news.parquet")
        try:
            return pl.scan_parquet(pattern).collect().sort("published_at", descending=True).to_dicts()
        except Exception:
            return []

    def aggregate_count(self) -> int:
        pattern = str(self.data_dir / "parquet" / "prices" / "*" / "*" / "*" / "prices.parquet")
        try:
            with duckdb.connect() as connection:
                result = connection.execute(
                    "select count(*) as rows from read_parquet(?)",
                    [pattern],
                ).fetchone()
            return int(result[0]) if result else 0
        except Exception:
            return 0
