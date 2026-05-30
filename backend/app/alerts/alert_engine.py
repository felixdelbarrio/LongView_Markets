from __future__ import annotations

from typing import Any

from app.repositories import demo_repository


class AlertEngine:
    def list_alerts(self) -> list[dict[str, Any]]:
        return demo_repository.get_alerts()

    def create_alert(self, payload: dict[str, Any]) -> dict[str, Any]:
        title = str(payload.get("title", "Custom alert"))
        return {
            "id": f"custom-{abs(hash(title)) % 100000}",
            "title": title,
            "severity": payload.get("severity", "medium"),
            "category": payload.get("category", "custom"),
            "status": "new",
            "confidence": 0.7,
            "explanation": "User-defined alert stored in the local demo layer for v1.",
            "evidence": payload,
        }
