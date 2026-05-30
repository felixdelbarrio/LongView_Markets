from __future__ import annotations

from typing import Any

from app.repositories import demo_repository


class PriceRepository:
    def get_daily_prices(self, ticker: str) -> list[dict[str, Any]]:
        return demo_repository.get_prices(ticker)

    def latest_prices(self, tickers: list[str]) -> dict[str, dict[str, Any]]:
        return {
            ticker.upper(): latest
            for ticker in tickers
            if (latest := demo_repository.latest_price(ticker)) is not None
        }
