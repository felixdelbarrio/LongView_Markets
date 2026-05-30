from __future__ import annotations

from typing import Any

from app.repositories import demo_repository


class WatchlistEngine:
    def list_watchlists(self) -> list[dict[str, Any]]:
        return demo_repository.get_watchlists()

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": payload.get("id", "custom-watchlist"),
            "name": payload.get("name", "Custom"),
            "items": payload.get("items", []),
            "status": "created",
        }
