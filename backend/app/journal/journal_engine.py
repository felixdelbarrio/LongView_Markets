from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class JournalEngine:
    def list_entries(self) -> list[dict[str, Any]]:
        return []

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        return {
            "id": payload.get("id", "custom-journal-entry"),
            "status": "active",
            "created_at": now,
            "updated_at": now,
            **payload,
        }
