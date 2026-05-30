from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.generative.context_builder import GenerativeContextBuilder
from app.generative.generative_repository import GenerativeRepository
from app.generative.prompt_builder import PromptBuilder
from app.generative.prompt_registry import PromptRegistry
from app.generative.response_repair import ResponseRepair
from app.generative.response_validator import ResponseValidator


class GenerativeIngestionEngine:
    def __init__(self, db_path: Path) -> None:
        self.repository = GenerativeRepository(db_path)
        self.registry = PromptRegistry()

    def create_job(
        self,
        job_type: str,
        entity_type: str,
        entity_id: str,
        context: dict[str, Any],
        prompt_id: str | None = None,
    ) -> dict[str, Any]:
        selected_prompt_id = prompt_id or (
            "portfolio_context_analysis_v1"
            if entity_type == "portfolio"
            else "instrument_context_analysis_v1"
        )
        prompt = self.registry.get(selected_prompt_id)
        prompt_text = PromptBuilder().build(selected_prompt_id, context)
        now = datetime.now(UTC).isoformat()
        context_text = json.dumps(context, ensure_ascii=False, sort_keys=True)
        job = {
            "id": f"gen_{uuid.uuid4().hex[:12]}",
            "job_type": job_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "prompt_id": selected_prompt_id,
            "prompt_version": prompt["prompt_version"],
            "schema_id": prompt["schema_id"],
            "schema_version": prompt["schema_version"],
            "status": "prompt_ready",
            "created_at": now,
            "updated_at": now,
            "input_hash": hashlib.sha256(context_text.encode("utf-8")).hexdigest(),
            "context_json": context,
            "prompt_text": prompt_text,
            "raw_response": None,
            "validated_json": None,
            "repair_attempts": 0,
            "errors": [],
            "warnings": [],
        }
        return self.repository.save_job(job)

    def validate_response(self, job_id: str, raw_response: str) -> dict[str, Any]:
        job = self.repository.get_job(job_id)
        if job is None:
            raise LookupError(job_id)
        validation = ResponseValidator().validate(raw_response, job["schema_id"])
        updated = {
            **job,
            "raw_response": raw_response,
            "validated_json": (
                json.dumps(validation["data"], ensure_ascii=False) if validation["valid"] else None
            ),
            "status": "validated" if validation["valid"] else "repair_required",
            "errors": validation["errors"],
            "updated_at": datetime.now(UTC).isoformat(),
        }
        self.repository.save_job(updated)
        return validation

    def repair_json(self, job_id: str, raw_response: str) -> dict[str, Any]:
        job = self.repository.get_job(job_id)
        if job is None:
            raise LookupError(job_id)
        repaired = ResponseRepair().repair(raw_response, job["schema_id"])
        updated = {
            **job,
            "raw_response": repaired["raw"],
            "validated_json": (
                json.dumps(repaired["data"], ensure_ascii=False) if repaired["repaired"] else None
            ),
            "status": "repaired" if repaired["repaired"] else "repair_required",
            "repair_attempts": int(job.get("repair_attempts") or 0) + 1,
            "errors": repaired["errors"],
            "warnings": ["was_repaired"] if repaired["repaired"] else [],
            "updated_at": datetime.now(UTC).isoformat(),
        }
        self.repository.save_job(updated)
        return repaired

    def import_response(self, job_id: str, raw_response: str | None = None) -> dict[str, Any]:
        job = self.repository.get_job(job_id)
        if job is None:
            raise LookupError(job_id)
        payload = raw_response or job.get("validated_json") or job.get("raw_response")
        validation = ResponseValidator().validate(str(payload), job["schema_id"])
        if not validation["valid"]:
            return {"imported": False, "errors": validation["errors"]}
        confidence = self._extract_confidence(validation["data"])
        response = self.repository.save_response(
            {
                "id": f"gen_resp_{uuid.uuid4().hex[:12]}",
                "job_id": job_id,
                "entity_type": job["entity_type"],
                "entity_id": job["entity_id"],
                "schema_id": job["schema_id"],
                "prompt_id": job["prompt_id"],
                "generated_at": validation["data"].get("generated_at") or datetime.now(UTC).isoformat(),
                "raw_response": str(payload),
                "validated_json": validation["data"],
                "was_repaired": 1 if job.get("status") == "repaired" else 0,
                "repair_method": ("deterministic_local" if job.get("status") == "repaired" else None),
                "confidence": confidence,
                "data_kind": "generative_inference",
            }
        )
        self.repository.save_job({**job, "status": "imported", "updated_at": datetime.now(UTC).isoformat()})
        return {"imported": True, "response": response}

    def prepare_daily_context(
        self,
        portfolio: dict[str, Any],
        instruments: list[dict[str, Any]],
        news: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        builder = GenerativeContextBuilder()
        jobs = [
            self.create_job(
                "daily_portfolio_review",
                "portfolio",
                "real",
                builder.build("portfolio", "real", portfolio=portfolio, news=news),
            )
        ]
        for position in portfolio.get("top_positions", [])[:5]:
            ticker = str(position["ticker"])
            instrument = next(
                (item for item in instruments if item["ticker"] == ticker),
                {"ticker": ticker},
            )
            jobs.append(
                self.create_job(
                    "daily_instrument_review",
                    "instrument",
                    ticker,
                    builder.build(
                        "instrument",
                        ticker,
                        portfolio=portfolio,
                        instrument=instrument,
                        news=news,
                    ),
                )
            )
        return jobs

    def import_jsonl(self, text: str) -> dict[str, Any]:
        imported = 0
        failed = 0
        errors: list[dict[str, str]] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
                result = self.import_response(
                    payload["job_id"],
                    json.dumps(payload["response"], ensure_ascii=False),
                )
                if result["imported"]:
                    imported += 1
                else:
                    failed += 1
                    errors.append(
                        {
                            "job_id": payload.get("job_id", "unknown"),
                            "error": ",".join(result["errors"]),
                        }
                    )
            except (json.JSONDecodeError, KeyError) as exc:
                failed += 1
                errors.append({"job_id": "unknown", "error": str(exc)})
        return {"imported": imported, "failed": failed, "repaired": 0, "errors": errors}

    def _extract_confidence(self, value: Any) -> float:
        if isinstance(value, dict):
            if "confidence" in value:
                try:
                    return float(value["confidence"])
                except (TypeError, ValueError):
                    return 0.0
            for item in value.values():
                found = self._extract_confidence(item)
                if found:
                    return found
        if isinstance(value, list):
            for item in value:
                found = self._extract_confidence(item)
                if found:
                    return found
        return 0.0
