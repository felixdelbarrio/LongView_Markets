from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.db.database import ensure_database, get_connection


class GenerativeRepository:
    def __init__(self, db_path: Path) -> None:
        self.db_path = ensure_database(db_path)

    def save_job(self, job: dict[str, Any]) -> dict[str, Any]:
        row = {
            **job,
            "context_json": json.dumps(job.get("context_json", {}), ensure_ascii=False),
            "errors": json.dumps(job.get("errors", []), ensure_ascii=False),
            "warnings": json.dumps(job.get("warnings", []), ensure_ascii=False),
        }
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO generative_jobs(
                  id, job_type, entity_type, entity_id, prompt_id, prompt_version, schema_id,
                  schema_version, status, created_at, updated_at, input_hash, context_json,
                  prompt_text, raw_response, validated_json, repair_attempts, errors, warnings
                ) VALUES(
                  :id, :job_type, :entity_type, :entity_id, :prompt_id, :prompt_version, :schema_id,
                  :schema_version, :status, :created_at, :updated_at, :input_hash, :context_json,
                  :prompt_text, :raw_response, :validated_json, :repair_attempts, :errors, :warnings
                )
                """,
                row,
            )
        return self.get_job(job["id"]) or job

    def list_jobs(self) -> list[dict[str, Any]]:
        with get_connection(self.db_path) as connection:
            rows = connection.execute("SELECT * FROM generative_jobs ORDER BY created_at DESC").fetchall()
        return [self._decode_job(dict(row)) for row in rows]

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with get_connection(self.db_path) as connection:
            row = connection.execute("SELECT * FROM generative_jobs WHERE id = ?", (job_id,)).fetchone()
        return self._decode_job(dict(row)) if row else None

    def save_response(self, response: dict[str, Any]) -> dict[str, Any]:
        row = {
            **response,
            "validated_json": json.dumps(response["validated_json"], ensure_ascii=False),
        }
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO generative_responses(
                  id, job_id, entity_type, entity_id, schema_id, prompt_id, generated_at,
                  raw_response, validated_json, was_repaired, repair_method, confidence, data_kind
                ) VALUES(
                  :id, :job_id, :entity_type, :entity_id, :schema_id, :prompt_id, :generated_at,
                  :raw_response, :validated_json, :was_repaired, :repair_method, :confidence, :data_kind
                )
                """,
                row,
            )
        return response

    def history(self) -> list[dict[str, Any]]:
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                "SELECT * FROM generative_responses ORDER BY generated_at DESC"
            ).fetchall()
        return [{**dict(row), "validated_json": json.loads(row["validated_json"])} for row in rows]

    def _decode_job(self, row: dict[str, Any]) -> dict[str, Any]:
        row["context_json"] = json.loads(row.get("context_json") or "{}")
        row["errors"] = json.loads(row.get("errors") or "[]")
        row["warnings"] = json.loads(row.get("warnings") or "[]")
        return row
