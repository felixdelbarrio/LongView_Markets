from __future__ import annotations

from app.repositories import demo_repository


class NewsEngine:
    def list_news(self, ticker: str | None = None) -> list[dict[str, object]]:
        return demo_repository.get_news(ticker)
