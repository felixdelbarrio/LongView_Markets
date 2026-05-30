from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb
import polars as pl


class ParquetRepository:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def read_prices(self, ticker: str) -> list[dict[str, Any]]:
        pattern = str(
            self.data_dir / "parquet" / "prices" / "*" / f"ticker={ticker}" / "*" / "prices.parquet"
        )
        try:
            return pl.scan_parquet(pattern).collect().to_dicts()
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
