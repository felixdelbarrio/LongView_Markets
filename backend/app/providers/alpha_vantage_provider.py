from __future__ import annotations

from datetime import date


class Provider:
    provider_name = "alpha_vantage"

    def search_instruments(self, query: str) -> list[dict[str, object]]:
        return []

    def get_daily_prices(
        self, ticker: str, start: date | None = None, end: date | None = None
    ) -> list[dict[str, object]]:
        return []

    def get_dividends(self, ticker: str) -> list[dict[str, object]]:
        return []

    def get_company_profile(self, ticker: str) -> dict[str, object] | None:
        return None
