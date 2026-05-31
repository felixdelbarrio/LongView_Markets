from __future__ import annotations

from typing import Any


class PortfolioRiskModel:
    def score(self, portfolio: dict[str, Any]) -> dict[str, Any]:
        flags = portfolio.get("risk_flags", [])
        return {"risk_score": min(100, 35 + len(flags) * 15), "risk_flags": flags}
