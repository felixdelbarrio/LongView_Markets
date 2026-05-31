from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class GenerativeContextBuilder:
    def build(
        self,
        entity_type: str,
        entity_id: str,
        portfolio: dict[str, Any] | None = None,
        instrument: dict[str, Any] | None = None,
        news: list[dict[str, Any]] | None = None,
        forecasts: list[dict[str, Any]] | None = None,
        alerts: list[dict[str, Any]] | None = None,
        data_quality: list[dict[str, Any]] | None = None,
        include_sensitive: bool = False,
    ) -> dict[str, Any]:
        context: dict[str, Any] = {
            "context_version": "1.0.0",
            "as_of": datetime.now(UTC).isoformat(),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "base_currency": (portfolio or {}).get("base_currency", "EUR"),
            "portfolio": self._portfolio_context(portfolio or {}, include_sensitive),
            "instrument": instrument or {},
            "news": self._limit(news or []),
            "forecasts": self._limit(forecasts or []),
            "alerts": self._limit(alerts or []),
            "data_quality": self._limit(data_quality or []),
            "privacy": {
                "sensitive_details_included": include_sensitive,
                "secrets_included": False,
                "data_kind": "structured_context",
            },
        }
        return context

    def _portfolio_context(self, portfolio: dict[str, Any], include_sensitive: bool) -> dict[str, Any]:
        positions = portfolio.get("positions", [])
        safe_positions = []
        for position in positions:
            safe_positions.append(
                {
                    "ticker": position.get("ticker"),
                    "weight": position.get("weight"),
                    "currency": position.get("currency"),
                    "sector": position.get("sector"),
                    "country": position.get("country"),
                    **({"market_value_base": position.get("market_value_base")} if include_sensitive else {}),
                }
            )
        return {
            "portfolio_id": portfolio.get("portfolio_id", "real"),
            "total_return_pct": portfolio.get("total_return_pct"),
            "risk_flags": portfolio.get("risk_flags", []),
            "positions": safe_positions[:25],
        }

    def _limit(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return rows[:50]
