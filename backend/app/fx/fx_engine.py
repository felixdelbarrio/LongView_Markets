from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from app.repositories.fx_repository import FxRepository


class FxEngine:
    def __init__(self, db_path: Path, base_currency: str = "EUR") -> None:
        self.repository = FxRepository(db_path, base_currency)

    def convert(self, amount: float, currency: str, on_date: date | None = None) -> dict[str, Any]:
        rate = self.repository.get_rate(currency, on_date)
        return {
            **rate,
            "amount": amount,
            "currency": currency.upper(),
            "converted_amount": round(amount * float(rate["rate"]), 4),
        }

    def supported_rates(self) -> list[dict[str, Any]]:
        return self.repository.list_supported()
