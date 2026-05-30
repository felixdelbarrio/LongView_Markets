from __future__ import annotations

import builtins
from typing import Any

from app.repositories import demo_repository


class InstrumentRepository:
    def list(self) -> builtins.list[dict[str, Any]]:
        return demo_repository.get_instruments()

    def get(self, ticker: str) -> dict[str, Any] | None:
        return demo_repository.get_instrument(ticker)

    def search(self, query: str) -> builtins.list[dict[str, Any]]:
        normalized = query.lower()
        return [
            item
            for item in self.list()
            if normalized in item["ticker"].lower() or normalized in item["name"].lower()
        ]
