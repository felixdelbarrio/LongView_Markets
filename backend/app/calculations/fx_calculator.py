from __future__ import annotations

from datetime import date
from typing import cast

DEFAULT_EUR_RATES: dict[str, float] = {
    "EUR": 1.0,
    "USD": 0.92,
    "GBP": 1.17,
    "CHF": 1.02,
    "JPY": 0.0059,
    "SEK": 0.088,
    "NOK": 0.087,
    "DKK": 0.134,
}


class FxCalculator:
    def __init__(self, base_currency: str = "EUR", rates: dict[str, float] | None = None) -> None:
        self.base_currency = base_currency.upper()
        self.rates = {**DEFAULT_EUR_RATES, **(rates or {})}

    def rate_to_base(self, currency: str, on_date: date | None = None) -> dict[str, object]:
        normalized = currency.upper()
        if normalized == self.base_currency:
            rate = 1.0
        elif self.base_currency == "EUR":
            rate = self.rates.get(normalized, 1.0)
        else:
            eur_value = self.rates.get(normalized, 1.0)
            target = self.rates.get(self.base_currency, 1.0)
            rate = eur_value / target if target else eur_value
        return {
            "rate": round(rate, 8),
            "date": (on_date or date.today()).isoformat(),
            "data_kind": "cached",
            "quality_flag": ("stale_fx" if normalized != self.base_currency else "observed_fx"),
            "provider": "yfinance-cache",
        }

    def convert(self, amount: float, currency: str, on_date: date | None = None) -> dict[str, object]:
        fx = self.rate_to_base(currency, on_date)
        rate = cast(float, fx["rate"])
        return {
            **fx,
            "amount": amount,
            "currency": currency.upper(),
            "base_currency": self.base_currency,
            "converted": round(amount * rate, 4),
        }
