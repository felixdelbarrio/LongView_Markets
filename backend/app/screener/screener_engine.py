from __future__ import annotations

from typing import Any


class ScreenerEngine:
    presets = [
        "Dividendos proximos",
        "Momentum saludable",
        "Drawdown interesante",
        "Baja volatilidad",
        "Cartera defensiva",
        "Alta incertidumbre, revisar",
    ]

    def screen(
        self, instruments: list[dict[str, Any]], analytics_by_ticker: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for instrument in instruments:
            metrics = analytics_by_ticker.get(instrument["ticker"], {}).get("metrics", {})
            rows.append(
                {
                    "ticker": instrument["ticker"],
                    "name": instrument["name"],
                    "country": instrument["country"],
                    "sector": instrument["sector"],
                    "currency": instrument["currency"],
                    "data_quality_score": instrument["data_quality_score"],
                    "cagr": metrics.get("cagr", 0),
                    "volatility": metrics.get("volatility", 0),
                    "drawdown": metrics.get("current_drawdown", 0),
                    "momentum": metrics.get("trend", "unknown"),
                    "dividend_yield": metrics.get("dividend_yield", 0),
                    "source": instrument["provider"],
                    "last_updated_at": instrument["last_updated_at"],
                    "confidence": instrument["confidence"],
                }
            )
        return sorted(rows, key=lambda item: (item["data_quality_score"], item["cagr"]), reverse=True)
