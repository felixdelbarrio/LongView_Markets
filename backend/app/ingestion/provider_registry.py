from __future__ import annotations

from typing import Any

from app.providers.stooq_provider import Provider as StooqProvider
from app.providers.yfinance_provider import Provider as YFinanceProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self.providers = {
            "yfinance": YFinanceProvider(),
            "stooq": StooqProvider(),
        }

    def get(self, provider_name: str) -> Any:
        return self.providers.get(provider_name, self.providers["yfinance"])

    def status(self) -> list[dict[str, Any]]:
        configured = set(self.providers)
        planned = [
            "yfinance",
            "stooq",
            "alpha_vantage",
            "finnhub",
            "twelve_data",
            "polygon",
            "bloomberg",
            "refinitiv",
            "factset",
        ]
        return [
            {
                "name": name,
                "status": "ready" if name in configured else "not_configured",
                "data_kind": "observed" if name == "yfinance" else "cached",
                "mock_fallback_available": False,
            }
            for name in planned
        ]
