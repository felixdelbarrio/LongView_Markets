from __future__ import annotations

import json
from typing import Any

from app.copilot.prompt_templates import DEFAULT_EXTERNAL_GPT_PROMPT


class CopilotContextBuilder:
    def build(
        self,
        ticker: str,
        instrument: dict[str, Any],
        analytics: dict[str, Any],
        news: list[dict[str, Any]],
        settings: dict[str, Any],
    ) -> dict[str, Any]:
        context = {
            "product": "LongView Markets",
            "disclaimer": "Informational and educational only. No financial, fiscal or legal advice.",
            "ticker": ticker,
            "instrument": instrument,
            "analytics": analytics,
            "news": news[:5],
            "settings": settings,
            "rules": [
                "Do not give absolute buy or sell instructions.",
                "Separate observed data, calculations, inferences, risks, scenarios and forecasts.",
                "Mention source, date, data kind and confidence.",
            ],
        }
        return {
            "ticker": ticker,
            "external_gpt_url": settings.get("external_gpt_url"),
            "prompt": DEFAULT_EXTERNAL_GPT_PROMPT,
            "context": context,
            "copyable_context": json.dumps(context, indent=2, ensure_ascii=False),
        }
