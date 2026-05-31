from __future__ import annotations

from typing import Any


class PortfolioNewsImpactEngine:
    def prioritize(self, portfolio: dict[str, Any], news: list[dict[str, Any]]) -> list[dict[str, Any]]:
        weights = {
            position["ticker"]: position.get("weight", 0) for position in portfolio.get("positions", [])
        }
        rows: list[dict[str, Any]] = []
        for item in news:
            tickers = item.get("tickers", [])
            ticker = str(tickers[0]) if tickers else ""
            rows.append(
                {
                    "ticker": ticker,
                    "headline": item.get("headline", ""),
                    "source": item.get("source", ""),
                    "published_at": item.get("published_at", ""),
                    "summary": item.get("summary", ""),
                    "portfolio_weight": weights.get(ticker, 0),
                    "possible_impact": "Revisar si afecta tesis, riesgo o timing de dividendos.",
                    "confidence": item.get("confidence", 0.6),
                    "explanation": "Priorizado por peso en cartera, alertas y disponibilidad de contexto.",
                    "generative_context_available": True,
                    "data_kind": "observed_or_cached",
                }
            )
        return sorted(rows, key=lambda row: float(row["portfolio_weight"]), reverse=True)
