from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.db.database import ensure_database, get_connection


class LocalRepository:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def all(self) -> list[dict[str, Any]]:
        return list(self.rows)

    def add(self, row: dict[str, Any]) -> dict[str, Any]:
        self.rows.append(row)
        return row


class PortfolioRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = ensure_database(db_path)

    def list_transactions(
        self, portfolio_id: str = "real", portfolio_type: str = "real"
    ) -> list[dict[str, Any]]:
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT * FROM portfolio_transactions
                WHERE portfolio_id = ? AND portfolio_type = ?
                  AND (? OR notes NOT LIKE '%Demo position created by LongView seed data%')
                ORDER BY trade_date ASC, created_at ASC
                """,
                (portfolio_id, portfolio_type, get_settings().demo_mode_enabled),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_transaction(self, payload: dict[str, Any], portfolio_type: str = "real") -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        transaction_type = str(payload.get("transaction_type", "buy")).lower()
        quantity = float(payload.get("quantity") or 0)
        price = float(payload.get("price") or 0)
        gross_amount = float(payload.get("gross_amount") or quantity * price)
        trade_date = str(payload.get("trade_date") or payload.get("date") or date.today().isoformat())[:10]
        row = {
            "id": str(payload.get("id") or f"txn_{uuid.uuid4().hex[:12]}"),
            "portfolio_id": str(
                payload.get("portfolio_id") or ("simulated" if portfolio_type == "simulated" else "real")
            ),
            "portfolio_type": portfolio_type,
            "ticker": str(payload.get("ticker", "")).upper(),
            "instrument_name": str(
                payload.get("instrument_name") or payload.get("name") or payload.get("ticker", "")
            ).strip(),
            "transaction_type": transaction_type,
            "quantity": quantity,
            "price": price,
            "gross_amount": gross_amount,
            "currency": str(payload.get("currency") or "EUR").upper(),
            "fees": float(payload.get("fees") or 0),
            "taxes": float(payload.get("taxes") or 0),
            "broker": str(payload.get("broker") or ""),
            "trade_date": trade_date,
            "settlement_date": str(payload.get("settlement_date") or trade_date)[:10],
            "source": str(payload.get("source") or "manual"),
            "requires_review": 1 if payload.get("requires_review") else 0,
            "notes": str(payload.get("notes") or ""),
            "created_at": now,
            "updated_at": now,
        }
        if not row["ticker"]:
            raise ValueError("ticker is required")
        if transaction_type in {"buy", "sell"} and quantity <= 0:
            raise ValueError("quantity must be positive for buy/sell transactions")
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO portfolio_transactions(
                  id, portfolio_id, portfolio_type, ticker, instrument_name, transaction_type,
                  quantity, price, gross_amount, currency, fees, taxes, broker, trade_date,
                  settlement_date, source, requires_review, notes, created_at, updated_at
                )
                VALUES(
                  :id, :portfolio_id, :portfolio_type, :ticker, :instrument_name, :transaction_type,
                  :quantity, :price, :gross_amount, :currency, :fees, :taxes, :broker, :trade_date,
                  :settlement_date, :source, :requires_review, :notes, :created_at, :updated_at
                )
                """,
                row,
            )
        return row

    def update_transaction(self, transaction_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        existing = self.get_transaction(transaction_id)
        if existing is None:
            raise LookupError(transaction_id)
        updated = {
            **existing,
            **payload,
            "id": transaction_id,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                UPDATE portfolio_transactions
                SET ticker=:ticker, instrument_name=:instrument_name, transaction_type=:transaction_type,
                    quantity=:quantity, price=:price, gross_amount=:gross_amount, currency=:currency,
                    fees=:fees, taxes=:taxes, broker=:broker, trade_date=:trade_date,
                    settlement_date=:settlement_date, source=:source, requires_review=:requires_review,
                    notes=:notes, updated_at=:updated_at
                WHERE id=:id
                """,
                updated,
            )
        return updated

    def delete_transaction(self, transaction_id: str) -> bool:
        with get_connection(self.db_path) as connection:
            cursor = connection.execute("DELETE FROM portfolio_transactions WHERE id = ?", (transaction_id,))
        return cursor.rowcount > 0

    def get_transaction(self, transaction_id: str) -> dict[str, Any] | None:
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT * FROM portfolio_transactions WHERE id = ?",
                (transaction_id,),
            ).fetchone()
        return dict(row) if row else None

    def seed_if_empty(self, transactions: list[dict[str, Any]]) -> None:
        if self.list_transactions():
            return
        for row in transactions:
            self.add_transaction(
                {
                    **row,
                    "trade_date": row.get("trade_date") or row.get("date"),
                    "instrument_name": row.get("ticker", ""),
                }
            )
