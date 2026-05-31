from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from app.calculations.fx_calculator import FxCalculator
from app.db.database import ensure_database


class FxRepository:
    def __init__(self, db_path: Path, base_currency: str = "EUR") -> None:
        self.db_path = ensure_database(db_path)
        self.calculator = FxCalculator(base_currency)

    def get_rate(self, currency: str, on_date: date | None = None) -> dict[str, Any]:
        return self.calculator.rate_to_base(currency, on_date)

    def list_supported(self) -> list[dict[str, Any]]:
        return [
            {"currency": currency, **self.calculator.rate_to_base(currency)}
            for currency in ["EUR", "USD", "GBP", "CHF", "JPY", "SEK", "NOK", "DKK"]
        ]
