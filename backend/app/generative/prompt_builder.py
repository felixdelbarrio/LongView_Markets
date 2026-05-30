from __future__ import annotations

import json
from typing import Any

from app.generative.prompt_registry import PromptRegistry
from app.generative.schemas import get_schema


class PromptBuilder:
    def build(self, prompt_id: str, context: dict[str, Any]) -> str:
        prompt = PromptRegistry().get(prompt_id)
        schema = get_schema(prompt["schema_id"])
        context_json = json.dumps(context, ensure_ascii=False, sort_keys=True)
        schema_json = json.dumps(schema, ensure_ascii=False, sort_keys=True)
        return (
            f"{prompt['system_instruction']}\n\n"
            f"JSON Schema obligatorio:\n{schema_json}\n\n"
            f"{prompt['user_template'].format(context_json=context_json)}"
        )
