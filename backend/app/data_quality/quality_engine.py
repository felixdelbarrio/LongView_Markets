from __future__ import annotations

from typing import Any

from app.data_quality.validators import validate_ohlc


class QualityEngine:
    def evaluate(
        self, instruments: list[dict[str, Any]], prices_by_ticker: dict[str, list[dict[str, Any]]]
    ) -> dict[str, Any]:
        issues: list[dict[str, Any]] = []
        provider_scores: dict[str, list[float]] = {}
        for instrument in instruments:
            ticker = instrument["ticker"]
            rows = prices_by_ticker.get(ticker, [])
            provider_scores.setdefault(instrument["provider"], []).append(instrument["data_quality_score"])
            seen_dates: set[str] = set()
            for row in rows[-260:]:
                for warning in validate_ohlc(row):
                    issues.append(
                        {"ticker": ticker, "issue": warning, "date": row["date"], "severity": "high"}
                    )
                if row["date"] in seen_dates:
                    issues.append(
                        {
                            "ticker": ticker,
                            "issue": "duplicate_date",
                            "date": row["date"],
                            "severity": "medium",
                        }
                    )
                seen_dates.add(row["date"])
            if rows and rows[-1]["date"] < "2026-05-01":
                issues.append(
                    {"ticker": ticker, "issue": "stale_data", "date": rows[-1]["date"], "severity": "high"}
                )
        provider_status = {
            provider: {"score": round(sum(scores) / len(scores), 2), "status": "ready"}
            for provider, scores in provider_scores.items()
        }
        global_score = round(
            sum(item["data_quality_score"] for item in instruments) / max(len(instruments), 1), 2
        )
        return {
            "global_score": global_score,
            "status": "ready" if global_score >= 85 else "review",
            "providers": provider_status,
            "issues": issues[:50],
            "data_kind": "mock",
            "explanation": "Quality checks cover missing data, duplicates, OHLC consistency and stale data.",
        }
