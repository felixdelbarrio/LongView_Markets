from __future__ import annotations

from app.repositories import demo_repository


class MockProvider:
    def search_instruments(self, query: str) -> list[dict[str, object]]:
        normalized = query.lower()
        return [
            item
            for item in demo_repository.get_instruments()
            if normalized in item["ticker"].lower() or normalized in item["name"].lower()
        ]

    def get_daily_prices(self, ticker: str) -> list[dict[str, object]]:
        return demo_repository.get_prices(ticker)

    def get_dividends(self, ticker: str) -> list[dict[str, object]]:
        return demo_repository.get_dividends(ticker)

    def get_company_profile(self, ticker: str) -> dict[str, object] | None:
        return demo_repository.get_instrument(ticker)
