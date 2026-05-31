from __future__ import annotations

from typing import Any


class AnomalyDetection:
    def detect(self, portfolio: dict[str, Any]) -> list[dict[str, Any]]:
        anomalies: list[dict[str, Any]] = []
        if "position_weight_high" in portfolio.get("risk_flags", []):
            anomalies.append({"type": "concentration_excessive", "severity": "medium"})
        if "currency_exposure_high" in portfolio.get("risk_flags", []):
            anomalies.append({"type": "currency_exposure_high", "severity": "medium"})
        return anomalies
