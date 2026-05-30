from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, cast


class ForecastingEngine:
    model_version = "longview-baseline-0.1.0"

    def forecast(self, ticker: str, prices: list[dict[str, Any]], horizon_days: int = 90) -> dict[str, Any]:
        if len(prices) < 60:
            return {"status": "insufficient_data", "ticker": ticker}
        closes = [float(row["adjusted_close"]) for row in prices[-120:]]
        slope = (closes[-1] - closes[0]) / len(closes)
        last = closes[-1]
        scenarios = []
        for scenario, multiplier in [
            ("adverse", 0.35),
            ("central", 1.0),
            ("optimistic", 1.55),
        ]:
            path = []
            for day in range(1, horizon_days + 1, 7):
                expected = max(0.1, last + slope * day * multiplier)
                path.append(
                    {
                        "date": (datetime.now(UTC).date() + timedelta(days=day)).isoformat(),
                        "value": round(expected, 2),
                    }
                )
                final_expected = cast(float, path[-1]["value"])
                scenarios.append(
                    {
                        "ticker": ticker,
                        "model_name": "moving-average-linear-baseline",
                        "model_version": self.model_version,
                        "generated_at": datetime.now(UTC).isoformat(),
                        "horizon_days": horizon_days,
                        "scenario": scenario,
                        "expected_path": path,
                        "confidence_interval_low": round(final_expected * 0.88, 2),
                        "confidence_interval_high": round(final_expected * 1.12, 2),
                        "confidence": 0.62 if scenario == "central" else 0.48,
                        "limitations": [
                            "This forecast is an extrapolation, not a prediction.",
                            "It ignores shocks, earnings surprises and macro regime changes.",
                        ],
                        "data_kind": "forecast",
                    }
                )
        return {"status": "ok", "ticker": ticker, "scenarios": scenarios}

    def detect_regime(self, prices: list[dict[str, Any]]) -> str:
        if len(prices) < 80:
            return "insufficient_history"
        recent = float(prices[-1]["adjusted_close"]) / float(prices[-40]["adjusted_close"]) - 1
        previous = float(prices[-40]["adjusted_close"]) / float(prices[-80]["adjusted_close"]) - 1
        if recent > 0 and previous < 0:
            return "recovery"
        if recent < 0 and previous > 0:
            return "deterioration"
        return "stable"
