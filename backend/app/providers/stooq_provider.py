from __future__ import annotations

from datetime import date

from app.repositories import demo_repository


class Provider:
    provider_name = "stooq"

    def search_instruments(self, query: str) -> list[dict[str, object]]:
        return [
            {**item, "provider": self.provider_name, "data_kind": "cache"}
            for item in demo_repository.get_instruments()
            if query.lower() in item["ticker"].lower() or query.lower() in item["name"].lower()
        ][:15]

    def get_daily_prices(
        self, ticker: str, start: date | None = None, end: date | None = None
    ) -> list[dict[str, object]]:
        rows = demo_repository.get_prices(ticker)
        return [
            {**row, "provider": self.provider_name, "data_kind": "cached"}
            for row in rows
            if (start is None or date.fromisoformat(row["date"]) >= start)
            and (end is None or date.fromisoformat(row["date"]) <= end)
        ]

    def get_dividends(self, ticker: str) -> list[dict[str, object]]:
        return demo_repository.get_dividends(ticker)

    def get_splits(self, ticker: str) -> list[dict[str, object]]:
        return []

    def get_company_profile(self, ticker: str) -> dict[str, object] | None:
        return demo_repository.get_instrument(ticker)

    def get_fx_rates(
        self, pair: str, start: date | None = None, end: date | None = None
    ) -> list[dict[str, object]]:
        return self.get_daily_prices(pair, start, end)
