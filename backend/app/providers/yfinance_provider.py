from __future__ import annotations

from datetime import UTC, date, datetime

from app.repositories import demo_repository


class Provider:
    provider_name = "yfinance"

    def search_instruments(self, query: str) -> list[dict[str, object]]:
        normalized = query.lower()
        return [
            {**item, "provider": self.provider_name, "data_kind": "observed_or_cache"}
            for item in demo_repository.get_instruments()
            if normalized in item["ticker"].lower() or normalized in item["name"].lower()
        ][:15]

    def get_daily_prices(
        self, ticker: str, start: date | None = None, end: date | None = None
    ) -> list[dict[str, object]]:
        try:
            import yfinance as yf

            frame = yf.download(
                ticker,
                start=start.isoformat() if start else None,
                end=end.isoformat() if end else None,
                progress=False,
                auto_adjust=False,
                threads=False,
            )
            if frame.empty:
                raise RuntimeError("empty yfinance frame")
            rows: list[dict[str, object]] = []
            for index, row in frame.tail(5000).iterrows():
                rows.append(
                    {
                        "date": index.date().isoformat(),
                        "ticker": ticker.upper(),
                        "open": float(row.get("Open", 0) or 0),
                        "high": float(row.get("High", 0) or 0),
                        "low": float(row.get("Low", 0) or 0),
                        "close": float(row.get("Close", 0) or 0),
                        "adjusted_close": float(row.get("Adj Close", row.get("Close", 0)) or 0),
                        "volume": int(row.get("Volume", 0) or 0),
                        "currency": (
                            self.get_company_profile(ticker).get("currency", "USD")
                            if self.get_company_profile(ticker)
                            else "USD"
                        ),
                        "provider": self.provider_name,
                        "data_kind": "observed",
                        "ingested_at": datetime.now(UTC).isoformat(),
                        "quality_score": 92,
                    }
                )
            return rows
        except Exception:
            return [
                {**row, "provider": self.provider_name, "data_kind": "mock_fallback"}
                for row in demo_repository.get_prices(ticker)
            ]

    def get_dividends(self, ticker: str) -> list[dict[str, object]]:
        try:
            import yfinance as yf

            dividends = yf.Ticker(ticker).dividends
            if dividends.empty:
                return []
            return [
                {
                    "ticker": ticker.upper(),
                    "ex_dividend_date": index.date().isoformat(),
                    "payment_date": index.date().isoformat(),
                    "amount": float(value),
                    "currency": (
                        self.get_company_profile(ticker).get("currency", "USD")
                        if self.get_company_profile(ticker)
                        else "USD"
                    ),
                    "dividend_type": "regular",
                    "provider": self.provider_name,
                    "ingested_at": datetime.now(UTC).isoformat(),
                    "quality_score": 90,
                    "data_kind": "observed",
                }
                for index, value in dividends.tail(120).items()
            ]
        except Exception:
            return demo_repository.get_dividends(ticker)

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

    def get_company_profile(self, ticker: str) -> dict[str, object]:
        instrument = demo_repository.get_instrument(ticker)
        if instrument:
            return {**instrument, "provider": self.provider_name}
        return {
            "ticker": ticker.upper(),
            "name": ticker.upper(),
            "currency": "USD",
            "provider": self.provider_name,
            "data_kind": "observed_or_cache",
        }

    def get_fx_rates(
        self, pair: str, start: date | None = None, end: date | None = None
    ) -> list[dict[str, object]]:
        return self.get_daily_prices(pair, start, end)
