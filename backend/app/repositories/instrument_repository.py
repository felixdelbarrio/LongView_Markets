from __future__ import annotations

import builtins
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.db.database import ensure_database, get_connection


class InstrumentRepository:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = ensure_database(db_path or get_settings().database_path)

    def list(self) -> builtins.list[dict[str, Any]]:
        with get_connection(self.db_path) as connection:
            rows = connection.execute("SELECT * FROM instruments ORDER BY ticker").fetchall()
        return [self._decode(dict(row)) for row in rows]

    def get(self, ticker: str) -> dict[str, Any] | None:
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM instruments WHERE ticker = ?",
                (ticker.upper(),),
            ).fetchone()
        return self._decode(dict(row)) if row else None

    def search(self, query: str) -> builtins.list[dict[str, Any]]:
        normalized = query.lower()
        return [
            item
            for item in self.list()
            if normalized in item["ticker"].lower() or normalized in item["name"].lower()
        ]

    def upsert(self, payload: dict[str, Any]) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        row = {
            "ticker": str(payload.get("ticker", "")).upper(),
            "name": str(payload.get("name") or payload.get("shortName") or payload.get("ticker", "")).strip(),
            "market": str(payload.get("market") or payload.get("exchange") or "unknown"),
            "exchange": str(payload.get("exchange") or payload.get("market") or "unknown"),
            "country": str(payload.get("country") or "unknown"),
            "currency": str(payload.get("currency") or "USD").upper(),
            "sector": str(payload.get("sector") or "Unknown"),
            "industry": str(payload.get("industry") or "Unknown"),
            "provider": str(payload.get("provider") or "yfinance"),
            "data_kind": str(payload.get("data_kind") or "observed"),
            "updated_at": str(payload.get("updated_at") or now),
        }
        if not row["ticker"]:
            raise ValueError("ticker is required")
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO instruments(
                  ticker, name, market, exchange, country, currency, sector, industry,
                  provider, data_kind, updated_at
                ) VALUES(
                  :ticker, :name, :market, :exchange, :country, :currency, :sector, :industry,
                  :provider, :data_kind, :updated_at
                )
                ON CONFLICT(ticker) DO UPDATE SET
                  name=excluded.name,
                  market=excluded.market,
                  exchange=excluded.exchange,
                  country=excluded.country,
                  currency=excluded.currency,
                  sector=excluded.sector,
                  industry=excluded.industry,
                  provider=excluded.provider,
                  data_kind=excluded.data_kind,
                  updated_at=excluded.updated_at
                """,
                row,
            )
        return self._decode(row)

    def _decode(self, row: dict[str, Any]) -> dict[str, Any]:
        row.setdefault("data_quality_score", 0)
        row.setdefault("confidence", 0)
        row["last_updated_at"] = row.get("updated_at")
        return row
