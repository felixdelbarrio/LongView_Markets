from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.db.database import ensure_database, get_connection


class IngestionRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = ensure_database(db_path)

    def create_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        row = {
            "id": payload["id"],
            "type": payload.get("type", "sync"),
            "provider": payload.get("provider", "yfinance"),
            "universe_id": payload.get("universe_id"),
            "ticker": payload.get("ticker"),
            "started_at": payload.get("started_at", now),
            "finished_at": payload.get("finished_at", now),
            "status": payload.get("status", "completed"),
            "rows_prices": int(payload.get("rows_prices", 0)),
            "rows_dividends": int(payload.get("rows_dividends", 0)),
            "rows_news": int(payload.get("rows_news", 0)),
            "rows_fx": int(payload.get("rows_fx", 0)),
            "errors": json.dumps(payload.get("errors", [])),
            "warnings": json.dumps(payload.get("warnings", [])),
        }
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO ingestion_jobs(
                  id, type, provider, universe_id, ticker, started_at, finished_at, status,
                  rows_prices, rows_dividends, rows_news, rows_fx, errors, warnings
                ) VALUES(
                  :id, :type, :provider, :universe_id, :ticker, :started_at, :finished_at, :status,
                  :rows_prices, :rows_dividends, :rows_news, :rows_fx, :errors, :warnings
                )
                """,
                row,
            )
        return self._decode(row)

    def list_jobs(self) -> list[dict[str, Any]]:
        with get_connection(self.db_path) as connection:
            rows = connection.execute("SELECT * FROM ingestion_jobs ORDER BY started_at DESC").fetchall()
        return [self._decode(dict(row)) for row in rows]

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with get_connection(self.db_path) as connection:
            row = connection.execute("SELECT * FROM ingestion_jobs WHERE id = ?", (job_id,)).fetchone()
        return self._decode(dict(row)) if row else None

    def _decode(self, row: dict[str, Any]) -> dict[str, Any]:
        row["errors"] = json.loads(row.get("errors") or "[]")
        row["warnings"] = json.loads(row.get("warnings") or "[]")
        return row
