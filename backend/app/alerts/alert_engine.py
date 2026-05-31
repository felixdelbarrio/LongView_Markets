from __future__ import annotations

from typing import Any


class AlertEngine:
    def list_alerts(self) -> list[dict[str, Any]]:
        return []

    def create_alert(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = str(payload.get("title", "Custom alert"))
        return {
            "id": f"custom-{abs(hash(title)) % 100000}",
            "title": title,
            "severity": payload.get("severity", "medium"),
            "category": payload.get("category", "custom"),
            "status": "new",
            "confidence": 0.7,
            "explanation": "User-defined alert queued for the operational alert store.",
            "evidence": payload,
        }
