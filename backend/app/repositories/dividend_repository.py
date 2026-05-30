from __future__ import annotations

from typing import Any

from app.repositories import demo_repository


class DividendRepository:
    def list(self, ticker: str | None = None) -> list[dict[str, Any]]:
        return demo_repository.get_dividends(ticker)
