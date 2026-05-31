from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class WatchlistEngine:
    def list_watchlists(self) -> list[dict[str, Any]]:
        return []

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        return {
            "id": payload.get("id", "custom-watchlist"),
            "name": payload.get("name", "Custom"),
            "items": payload.get("items", []),
            "created_at": now,
            "updated_at": now,
            "status": "created",
        }
