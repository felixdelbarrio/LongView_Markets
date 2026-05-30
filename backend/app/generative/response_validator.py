from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.generative.schemas import get_schema


class ResponseValidator:
    def validate(self, raw_response: str | dict[str, Any], schema_id: str) -> dict[str, Any]:
        errors: list[str] = []
        if isinstance(raw_response, str):
            try:
                payload = json.loads(raw_response)
            except json.JSONDecodeError as exc:
                return {
                    "valid": False,
                    "errors": [f"invalid_json:{exc.msg}"],
                    "data": None,
                }
        else:
            payload = raw_response
        schema = get_schema(schema_id)
        for field in schema.get("required", []):
            if field not in payload:
                errors.append(f"missing_required:{field}")
        if payload.get("not_financial_advice") is not True:
            errors.append("not_financial_advice_must_be_true")
        generated_at = payload.get("generated_at")
        if generated_at:
            try:
                datetime.fromisoformat(str(generated_at).replace("Z", "+00:00"))
            except ValueError:
                errors.append("generated_at_must_be_iso8601")
        self._check_confidence(payload, errors)
        return {
            "valid": not errors,
            "errors": errors,
            "data": payload if not errors else None,
        }

    def _check_confidence(self, value: Any, errors: list[str]) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "confidence":
                    try:
                        numeric = float(item)
                    except (TypeError, ValueError):
                        errors.append("confidence_must_be_number")
                        continue
                    if numeric < 0 or numeric > 1:
                        errors.append("confidence_out_of_range")
                else:
                    self._check_confidence(item, errors)
        elif isinstance(value, list):
            for item in value:
                self._check_confidence(item, errors)
