from __future__ import annotations

from typing import Any


class LocalRepository:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def all(self) -> list[dict[str, Any]]:
        return list(self.rows)

    def add(self, row: dict[str, Any]) -> dict[str, Any]:
        self.rows.append(row)
        return row
