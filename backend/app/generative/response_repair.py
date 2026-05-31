from __future__ import annotations

import json
import re
from typing import Any

from app.generative.response_validator import ResponseValidator


class ResponseRepair:
    def repair(self, raw_response: str, schema_id: str) -> dict[str, Any]:
        repaired = raw_response.strip()
        repaired = re.sub(r"^```(?:json)?", "", repaired).strip()
        repaired = re.sub(r"```$", "", repaired).strip()
        if "{" in repaired and "}" in repaired:
            repaired = repaired[repaired.find("{") : repaired.rfind("}") + 1]
        repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
        try:
            payload = json.loads(repaired)
        except json.JSONDecodeError as exc:
            return {
                "repaired": False,
                "raw": repaired,
                "errors": [f"repair_failed:{exc.msg}"],
                "data": None,
            }
        validation = ResponseValidator().validate(payload, schema_id)
        return {
            "repaired": validation["valid"],
            "raw": json.dumps(payload, ensure_ascii=False),
            "errors": validation["errors"],
            "data": validation["data"],
            "repair_method": "deterministic_local",
        }
