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
        return [
            {
                "name": name,
                "status": "ready",
                "data_kind": "observed" if name == "yfinance" else "cached",
                "mock_fallback_available": True,
            }
            for name in self.providers
        ]
