from __future__ import annotations

from typing import Any

from app.repositories import demo_repository


class JournalEngine:
    def list_entries(self) -> list[dict[str, Any]]:
        return demo_repository.get_journal_entries()

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"id": payload.get("id", "custom-journal-entry"), "status": "active", **payload}
