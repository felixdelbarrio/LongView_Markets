from __future__ import annotations

from pathlib import Path

from app.db.database import ensure_database


def migrate(db_path: Path) -> Path:
    return ensure_database(db_path)
