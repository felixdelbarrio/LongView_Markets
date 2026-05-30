from __future__ import annotations

from typing import Any


class FeatureStore:
    def instrument_features(self, ticker: str, prices: list[dict[str, Any]]) -> dict[str, Any]:
        closes = [float(row.get("adjusted_close") or row.get("close") or 0) for row in prices[-260:]]
        last = closes[-1] if closes else 0
        first = closes[0] if closes else last
        peak = max(closes) if closes else last
        return {
            "ticker": ticker,
            "daily_return": ((closes[-1] / closes[-2] - 1) if len(closes) > 1 and closes[-2] else 0),
            "rolling_return_20d": ((last / closes[-20] - 1) if len(closes) >= 20 and closes[-20] else 0),
            "rolling_return_60d": ((last / closes[-60] - 1) if len(closes) >= 60 and closes[-60] else 0),
            "drawdown": (last / peak - 1) if peak else 0,
            "distance_to_52w_high": (last / peak - 1) if peak else 0,
            "moving_average_50": (sum(closes[-50:]) / min(len(closes), 50) if closes else 0),
            "moving_average_200": (sum(closes[-200:]) / min(len(closes), 200) if closes else 0),
            "cashflow_adjusted_return": (last / first - 1) if first else 0,
        }
