from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.repositories.parquet_repository import ParquetRepository


class NewsRepository:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.parquet = ParquetRepository(data_dir or get_settings().data_dir)

    def list(self, ticker: str | None = None) -> list[dict[str, Any]]:
        return self.parquet.read_news(ticker)
