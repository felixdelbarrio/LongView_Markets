from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class UniverseLoader:
    def __init__(self, root: Path) -> None:
        self.root = root

    def list_universes(self) -> list[dict[str, Any]]:
        universes: list[dict[str, Any]] = []
        for path in sorted(self.root.glob("*.yml")):
            data = self.load(path.stem)
            universes.append(
                {
                    "id": path.stem,
                    "name": data.get("name", path.stem),
                    "description": data.get("description", ""),
                    "count": len(data.get("tickers", [])),
                    "data_kind": "configuration",
                }
            )
        return universes

    def load(self, universe_id: str) -> dict[str, Any]:
        path = self.root / f"{universe_id}.yml"
        if not path.exists():
            raise LookupError(universe_id)
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
