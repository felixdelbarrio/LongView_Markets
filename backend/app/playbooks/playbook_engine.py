from __future__ import annotations

from app.repositories import demo_repository


class PlaybookEngine:
    def list_playbooks(self) -> list[dict[str, object]]:
        return demo_repository.get_playbooks()
