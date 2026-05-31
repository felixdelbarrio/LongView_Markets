from __future__ import annotations

from app.providers.yfinance_provider import Provider as YFinanceProvider


class Provider(YFinanceProvider):
    provider_name = "yfinance"
