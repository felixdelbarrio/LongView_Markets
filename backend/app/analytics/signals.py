from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class SignalEngine:
    def build_signals(self, ticker: str, analytics: dict[str, Any]) -> list[dict[str, Any]]:
        metrics = analytics.get("metrics", {})
        signals: list[dict[str, Any]] = []
        if metrics.get("current_drawdown", 0) < -12:
            signals.append(
                self._signal(
                    ticker,
                    "Relevant drawdown",
                    "risk",
                    "medium",
                    {"current_drawdown": metrics.get("current_drawdown")},
                )
            )
        if metrics.get("moving_average_cross") == "bullish_50_200":
            signals.append(
                self._signal(
                    ticker,
                    "Bullish 50/200 moving-average structure",
                    "trend",
                    "low",
                    {"ma50": metrics.get("moving_average_50"), "ma200": metrics.get("moving_average_200")},
                )
            )
        if metrics.get("volatility", 0) > 28:
            signals.append(
                self._signal(
                    ticker,
                    "High recent volatility",
                    "risk",
                    "high",
                    {"volatility": metrics.get("volatility")},
                )
            )
        if metrics.get("dividend_yield", 0) > 2:
            signals.append(
                self._signal(
                    ticker,
                    "Forward dividend yield visible",
                    "income",
                    "medium",
                    {"dividend_yield": metrics.get("dividend_yield")},
                )
            )
        if not signals:
            signals.append(
                self._signal(
                    ticker,
                    "Stable long-term review candidate",
                    "quality",
                    "low",
                    {"trend": metrics.get("trend")},
                )
            )
        return signals

    def _signal(
        self, ticker: str, title: str, category: str, severity: str, evidence: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "id": f"{ticker}-{title.lower().replace(' ', '-')}",
            "ticker": ticker,
            "title": title,
            "category": category,
            "severity": severity,
            "explanation": "Generated from backend-only metrics with source, confidence and limitations attached.",
            "formula": "LongView deterministic rule over calculated metrics.",
            "evidence": evidence,
            "confidence": 0.78,
            "generated_at": datetime.now(UTC).isoformat(),
            "data_sources": ["LongView deterministic seed"],
            "limitations": ["Demo data, not investment advice."],
        }
