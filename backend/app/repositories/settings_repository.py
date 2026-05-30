from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.db.database import ensure_database, get_connection


class LocalRepository:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def all(self) -> list[dict[str, Any]]:
        return list(self.rows)

    def add(self, row: dict[str, Any]) -> dict[str, Any]:
        self.rows.append(row)
        return row


DEFAULT_SETTINGS: dict[str, Any] = {
    "language": "es",
    "theme": "dark",
    "base_currency": "EUR",
    "fiscal_country": "ES",
    "default_market_provider": "yfinance",
    "secondary_market_provider": "stooq",
    "news_provider": "rss",
    "fx_provider": "yfinance",
    "auto_sync_on_startup": False,
    "scheduled_sync_enabled": False,
    "scheduled_sync_time": "22:30",
    "sync_universes": "ibex35,eurostoxx50,stoxx_europe_600_sample,nasdaq100,sp500,dax40,cac40,ftse100,ftse_mib,aex25,smi20,psi20,ucits_etf_sample",
    "portfolio_cost_method": "FIFO",
    "mock_fallback_enabled": True,
    "demo_mode_enabled": False,
    "generative_enabled": True,
    "generative_mode": "manual_url",
    "external_gpt_url": "https://chatgpt.com/g/g-longview-markets",
    "generative_language": "es",
    "generative_prompt_depth": "standard",
    "generative_include_portfolio": True,
    "generative_include_news": True,
    "generative_include_forecasts": True,
    "generative_include_tax": False,
    "generative_include_data_quality": True,
    "generative_auto_prepare_daily_jobs": True,
    "generative_auto_import_allowed": False,
    "generative_json_repair_enabled": True,
    "generative_store_history": True,
    "generative_max_context_items": 50,
    "generative_confidence_threshold": 0.60,
    "generative_include_sensitive_portfolio_details": False,
}


class SettingsRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = ensure_database(db_path)
        self.ensure_defaults()

    def ensure_defaults(self) -> None:
        with get_connection(self.db_path) as connection:
            for key, value in DEFAULT_SETTINGS.items():
                connection.execute(
                    "INSERT OR IGNORE INTO settings(key, value, updated_at) VALUES (?, ?, ?)",
                    (key, self._serialize(value), datetime.now(UTC).isoformat()),
                )

    def get_all(self) -> dict[str, Any]:
        self.ensure_defaults()
        with get_connection(self.db_path) as connection:
            rows = connection.execute("SELECT key, value FROM settings").fetchall()
        return {row["key"]: self._deserialize(row["value"]) for row in rows}

    def update(self, payload: dict[str, Any]) -> dict[str, Any]:
        with get_connection(self.db_path) as connection:
            for key, value in payload.items():
                if key.startswith("_"):
                    continue
                connection.execute(
                    "INSERT OR REPLACE INTO settings(key, value, updated_at) VALUES (?, ?, ?)",
                    (key, self._serialize(value), datetime.now(UTC).isoformat()),
                )
        return self.get_all()

    def _serialize(self, value: Any) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def _deserialize(self, value: str) -> Any:
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value
