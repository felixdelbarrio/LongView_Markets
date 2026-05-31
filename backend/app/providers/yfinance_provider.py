from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any

from app.core.config import get_settings


class Provider:
    provider_name = "yfinance"

    def search_instruments(self, query: str) -> list[dict[str, object]]:
        if not query.strip():
            return []
        profile = self.get_company_profile(query.strip())
        return [profile] if profile else []

    def get_daily_prices(
        self, ticker: str, start: date | None = None, end: date | None = None
    ) -> list[dict[str, object]]:
        symbol = ticker.upper()
        start_date = start or (date.today() - timedelta(days=365 * 2 + 14))
        try:
            import pandas as pd
            import yfinance as yf

            frame = yf.download(
                symbol,
                start=start_date.isoformat(),
                end=end.isoformat() if end else None,
                progress=False,
                auto_adjust=False,
                threads=False,
            )
            if frame.empty:
                raise RuntimeError("empty yfinance frame")
            if isinstance(frame.columns, pd.MultiIndex):
                if symbol in frame.columns.get_level_values(-1):
                    frame = frame.xs(symbol, axis=1, level=-1)
                else:
                    frame.columns = frame.columns.get_level_values(0)
            profile = self.get_company_profile(symbol) or {}
            currency = str(profile.get("currency") or "USD").upper()
            rows: list[dict[str, object]] = []
            for index, row in frame.tail(5000).iterrows():
                rows.append(
                    {
                        "date": index.date().isoformat(),
                        "ticker": symbol,
                        "open": self._number(row.get("Open")),
                        "high": self._number(row.get("High")),
                        "low": self._number(row.get("Low")),
                        "close": self._number(row.get("Close")),
                        "adjusted_close": self._number(row.get("Adj Close", row.get("Close"))),
                        "volume": int(self._number(row.get("Volume"))),
                        "currency": currency,
                        "provider": self.provider_name,
                        "data_kind": "observed",
                        "ingested_at": datetime.now(UTC).isoformat(),
                        "quality_score": 92,
                    }
                )
            return rows
        except Exception:
            return self._demo_prices(symbol)

    def get_dividends(self, ticker: str) -> list[dict[str, object]]:
        symbol = ticker.upper()
        try:
            import yfinance as yf

            profile = self.get_company_profile(symbol) or {}
            currency = str(profile.get("currency") or "USD").upper()
            dividends = yf.Ticker(symbol).dividends
            if dividends.empty:
                return []
            return [
                {
                    "ticker": symbol,
                    "ex_dividend_date": index.date().isoformat(),
                    "payment_date": index.date().isoformat(),
                    "amount": float(value),
                    "currency": currency,
                    "dividend_type": "regular",
                    "provider": self.provider_name,
                    "ingested_at": datetime.now(UTC).isoformat(),
                    "quality_score": 90,
                    "data_kind": "observed",
                }
                for index, value in dividends.tail(120).items()
            ]
        except Exception:
            return self._demo_dividends(symbol)

    def get_news(self, ticker: str) -> list[dict[str, object]]:
        symbol = ticker.upper()
        try:
            import yfinance as yf

            news_rows = yf.Ticker(symbol).news or []
        except Exception:
            news_rows = []
        rows: list[dict[str, object]] = []
        for index, item in enumerate(news_rows[:40]):
            content = item.get("content", item) if isinstance(item, dict) else {}
            title = str(content.get("title") or item.get("title") or "")
            if not title:
                continue
            published_at = (
                content.get("pubDate") or content.get("displayTime") or datetime.now(UTC).isoformat()
            )
            rows.append(
                {
                    "id": str(content.get("id") or f"{symbol}_{index}"),
                    "ticker": symbol,
                    "headline": title,
                    "summary": str(content.get("summary") or ""),
                    "source": str((content.get("provider") or {}).get("displayName") or "yfinance"),
                    "url": str(
                        content.get("canonicalUrl", {}).get("url")
                        or content.get("clickThroughUrl", {}).get("url")
                        or ""
                    ),
                    "published_at": str(published_at),
                    "sentiment": "pending",
                    "confidence": 0.0,
                    "provider": self.provider_name,
                    "data_kind": "observed",
                }
            )
        return rows

    def get_splits(self, ticker: str) -> list[dict[str, object]]:
        try:
            import yfinance as yf

            splits = yf.Ticker(ticker).splits
            return [
                {
                    "ticker": ticker.upper(),
                    "date": index.date().isoformat(),
                    "ratio": float(value),
                    "provider": self.provider_name,
                    "ingested_at": datetime.now(UTC).isoformat(),
                    "data_kind": "observed",
                }
                for index, value in splits.tail(50).items()
            ]
        except Exception:
            return []

    def get_company_profile(self, ticker: str) -> dict[str, object] | None:
        symbol = ticker.upper()
        try:
            import yfinance as yf

            info = yf.Ticker(symbol).get_info() or {}
            return {
                "ticker": symbol,
                "name": info.get("longName") or info.get("shortName") or symbol,
                "market": info.get("market") or info.get("exchange") or "unknown",
                "exchange": info.get("exchange") or "unknown",
                "country": info.get("country") or "unknown",
                "currency": info.get("currency") or "USD",
                "sector": info.get("sector") or "Unknown",
                "industry": info.get("industry") or "Unknown",
                "provider": self.provider_name,
                "data_kind": "observed",
                "updated_at": datetime.now(UTC).isoformat(),
            }
        except Exception:
            return self._demo_profile(symbol)

    def get_fx_rates(
        self, pair: str, start: date | None = None, end: date | None = None
    ) -> list[dict[str, object]]:
        return self.get_daily_prices(pair, start, end)

    def _number(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _demo_prices(self, ticker: str) -> list[dict[str, object]]:
        settings = get_settings()
        if not (settings.demo_mode_enabled and settings.mock_fallback_enabled):
            return []
        from app.repositories import demo_repository

        return [
            {**row, "provider": self.provider_name, "data_kind": "mock"}
            for row in demo_repository.get_prices(ticker)
        ]

    def _demo_dividends(self, ticker: str) -> list[dict[str, object]]:
        settings = get_settings()
        if not (settings.demo_mode_enabled and settings.mock_fallback_enabled):
            return []
        from app.repositories import demo_repository

        return [
            {**row, "provider": self.provider_name, "data_kind": "mock"}
            for row in demo_repository.get_dividends(ticker)
        ]

    def _demo_profile(self, ticker: str) -> dict[str, object] | None:
        settings = get_settings()
        if not (settings.demo_mode_enabled and settings.mock_fallback_enabled):
            return {
                "ticker": ticker,
                "name": ticker,
                "market": "unknown",
                "exchange": "unknown",
                "country": "unknown",
                "currency": "USD",
                "sector": "Unknown",
                "industry": "Unknown",
                "provider": self.provider_name,
                "data_kind": "metadata_only",
                "updated_at": datetime.now(UTC).isoformat(),
            }
        from app.repositories import demo_repository

        instrument = demo_repository.get_instrument(ticker)
        return {**instrument, "provider": self.provider_name, "data_kind": "mock"} if instrument else None
