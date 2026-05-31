from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS instruments (
  ticker TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  market TEXT NOT NULL,
  exchange TEXT NOT NULL,
  country TEXT NOT NULL,
  currency TEXT NOT NULL,
  sector TEXT NOT NULL,
  industry TEXT NOT NULL,
  provider TEXT NOT NULL,
  data_kind TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolio_transactions (
  id TEXT PRIMARY KEY,
  portfolio_id TEXT NOT NULL,
  portfolio_type TEXT NOT NULL DEFAULT 'real',
  ticker TEXT NOT NULL,
  instrument_name TEXT NOT NULL DEFAULT '',
  transaction_type TEXT NOT NULL,
  quantity REAL NOT NULL DEFAULT 0,
  price REAL NOT NULL DEFAULT 0,
  gross_amount REAL NOT NULL DEFAULT 0,
  currency TEXT NOT NULL DEFAULT 'EUR',
  fees REAL NOT NULL DEFAULT 0,
  taxes REAL NOT NULL DEFAULT 0,
  broker TEXT NOT NULL DEFAULT '',
  trade_date TEXT NOT NULL,
  settlement_date TEXT,
  source TEXT NOT NULL DEFAULT 'manual',
  requires_review INTEGER NOT NULL DEFAULT 0,
  notes TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS simulated_transactions (
  id TEXT PRIMARY KEY,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alerts (
  id TEXT PRIMARY KEY,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS watchlists (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS watchlist_items (
  id TEXT PRIMARY KEY,
  watchlist_id TEXT NOT NULL,
  ticker TEXT NOT NULL,
  reason TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS journal_entries (
  id TEXT PRIMARY KEY,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ingestion_jobs (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  provider TEXT NOT NULL,
  universe_id TEXT,
  ticker TEXT,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  status TEXT NOT NULL,
  rows_prices INTEGER NOT NULL DEFAULT 0,
  rows_dividends INTEGER NOT NULL DEFAULT 0,
  rows_news INTEGER NOT NULL DEFAULT 0,
  rows_fx INTEGER NOT NULL DEFAULT 0,
  errors TEXT NOT NULL DEFAULT '[]',
  warnings TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS provider_status (
  provider TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  checked_at TEXT NOT NULL,
  details TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS screener_presets (
  id TEXT PRIMARY KEY,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generative_prompts (
  prompt_id TEXT PRIMARY KEY,
  prompt_version TEXT NOT NULL,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  schema_id TEXT NOT NULL,
  schema_version TEXT NOT NULL,
  language TEXT NOT NULL,
  system_instruction TEXT NOT NULL,
  user_template TEXT NOT NULL,
  output_contract TEXT NOT NULL,
  created_at TEXT NOT NULL,
  deprecated INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS generative_jobs (
  id TEXT PRIMARY KEY,
  job_type TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  prompt_id TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  schema_id TEXT NOT NULL,
  schema_version TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  input_hash TEXT NOT NULL,
  context_json TEXT NOT NULL,
  prompt_text TEXT NOT NULL,
  raw_response TEXT,
  validated_json TEXT,
  repair_attempts INTEGER NOT NULL DEFAULT 0,
  errors TEXT NOT NULL DEFAULT '[]',
  warnings TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS generative_responses (
  id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  schema_id TEXT NOT NULL,
  prompt_id TEXT NOT NULL,
  generated_at TEXT NOT NULL,
  raw_response TEXT NOT NULL,
  validated_json TEXT NOT NULL,
  was_repaired INTEGER NOT NULL DEFAULT 0,
  repair_method TEXT,
  confidence REAL NOT NULL DEFAULT 0,
  data_kind TEXT NOT NULL DEFAULT 'generative_inference'
);

CREATE TABLE IF NOT EXISTS generative_insights (
  id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  confidence REAL NOT NULL,
  source_response_id TEXT NOT NULL,
  created_at TEXT NOT NULL,
  data_kind TEXT NOT NULL DEFAULT 'generative_inference'
);

CREATE TABLE IF NOT EXISTS generative_context_snapshots (
  id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  context_json TEXT NOT NULL,
  input_hash TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prices_metadata (
  id TEXT PRIMARY KEY,
  ticker TEXT NOT NULL,
  provider TEXT NOT NULL,
  rows_count INTEGER NOT NULL DEFAULT 0,
  first_date TEXT,
  last_date TEXT,
  status TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS news_sentiment (
  id TEXT PRIMARY KEY,
  news_id TEXT NOT NULL,
  ticker TEXT NOT NULL,
  sentiment TEXT NOT NULL,
  impact TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS forecast_jobs (
  id TEXT PRIMARY KEY,
  ticker TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS forecast_results (
  id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL,
  ticker TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS screener_recommendations (
  id TEXT PRIMARY KEY,
  ticker TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS screener_recommendation_outcomes (
  id TEXT PRIMARY KEY,
  recommendation_id TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dividend_opportunities (
  id TEXT PRIMARY KEY,
  ticker TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dividend_actions (
  id TEXT PRIMARY KEY,
  ticker TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS data_quality_snapshots (
  id TEXT PRIMARY KEY,
  scope TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
"""


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


@contextmanager
def get_connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()


def ensure_database(db_path: Path) -> Path:
    with get_connection(db_path) as connection:
        connection.executescript(SCHEMA_SQL)
        connection.execute(
            "INSERT OR REPLACE INTO provider_status(provider, status, checked_at, details) VALUES (?, ?, ?, ?)",
            ("sqlite", "ready", now_iso(), '{"data_kind":"observed"}'),
        )
    return db_path
