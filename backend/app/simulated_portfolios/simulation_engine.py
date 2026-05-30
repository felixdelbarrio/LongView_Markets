from __future__ import annotations

from typing import Any

from app.portfolios.portfolio_engine import PortfolioEngine


class SimulationEngine(PortfolioEngine):
    def convert_to_real(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"status": "ready_for_review", "transaction": payload, "requires_confirmation": True}
