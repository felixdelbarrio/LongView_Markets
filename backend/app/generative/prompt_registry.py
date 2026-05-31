from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

BASE_SYSTEM_INSTRUCTION = """Eres un analista financiero prudente, esceptico y explicable.
No das recomendaciones absolutas de compra o venta. No prometes rentabilidad. No inventas datos.
Distingues claramente entre datos observados, calculos derivados, inferencias, riesgos, escenarios y predicciones.
Tu salida debe ser exclusivamente JSON valido. No incluyas markdown. No incluyas texto antes o despues del JSON.
No incluyas comentarios. No uses trailing commas. Respeta exactamente el JSON Schema proporcionado.
Si un dato no esta disponible, usa null. Si una lista no tiene elementos, usa [].
Todos los niveles de confianza deben estar entre 0 y 1. Incluye siempre limitaciones.
Incluye siempre not_financial_advice=true."""


PROMPTS: list[dict[str, Any]] = [
    {
        "prompt_id": "instrument_context_analysis_v1",
        "prompt_version": "1.0.0",
        "name": "Analisis contextual de instrumento",
        "description": "Evalua un valor con noticias, forecast y cartera sin sustituir calculos.",
        "schema_id": "instrument_context_analysis",
        "schema_version": "1.0.0",
        "language": "es",
        "system_instruction": BASE_SYSTEM_INSTRUCTION,
        "user_template": "Analiza el instrumento usando exclusivamente este contexto JSON: {context_json}",
        "output_contract": "JSON estricto validado contra instrument_context_analysis.",
        "created_at": datetime.now(UTC).isoformat(),
        "deprecated": False,
    },
    {
        "prompt_id": "portfolio_context_analysis_v1",
        "prompt_version": "1.0.0",
        "name": "Analisis contextual de cartera",
        "description": "Resume riesgos, cambios, oportunidades a revisar y limitaciones de cartera.",
        "schema_id": "portfolio_context_analysis",
        "schema_version": "1.0.0",
        "language": "es",
        "system_instruction": BASE_SYSTEM_INSTRUCTION,
        "user_template": "Analiza la cartera usando exclusivamente este contexto JSON: {context_json}",
        "output_contract": "JSON estricto validado contra portfolio_context_analysis.",
        "created_at": datetime.now(UTC).isoformat(),
        "deprecated": False,
    },
]

for prompt_id, schema_id, name in [
    ("daily_market_briefing_v1", "daily_market_briefing", "Briefing diario"),
    ("news_impact_analysis_v1", "news_impact_analysis", "Impacto de noticias"),
    ("forecast_explanation_v1", "forecast_explanation", "Explicacion de forecast"),
    ("alert_explanation_v1", "alert_explanation", "Explicacion de alerta"),
    (
        "dividend_strategy_review_v1",
        "dividend_strategy_analysis",
        "Revision de dividendos",
    ),
    ("investment_thesis_review_v1", "investment_thesis_review", "Revision de tesis"),
]:
    PROMPTS.append(
        {
            "prompt_id": prompt_id,
            "prompt_version": "1.0.0",
            "name": name,
            "description": "Prompt estructurado de LongView Markets.",
            "schema_id": schema_id,
            "schema_version": "1.0.0",
            "language": "es",
            "system_instruction": BASE_SYSTEM_INSTRUCTION,
            "user_template": "Usa exclusivamente este contexto JSON: {context_json}",
            "output_contract": f"JSON estricto validado contra {schema_id}.",
            "created_at": datetime.now(UTC).isoformat(),
            "deprecated": False,
        }
    )


class PromptRegistry:
    def list_prompts(self) -> list[dict[str, Any]]:
        return PROMPTS

    def get(self, prompt_id: str) -> dict[str, Any]:
        return next(prompt for prompt in PROMPTS if prompt["prompt_id"] == prompt_id)
