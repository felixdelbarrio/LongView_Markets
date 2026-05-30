from __future__ import annotations

from typing import Any

BASE_DEFINITIONS: dict[str, Any] = {
    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    "severity": {"enum": ["info", "low", "medium", "high", "critical"]},
    "priority": {"enum": ["low", "medium", "high", "critical"]},
}


INSTRUMENT_CONTEXT_ANALYSIS_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "instrument_context_analysis",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "prompt_version",
        "analysis_type",
        "ticker",
        "generated_at",
        "language",
        "executive_summary",
        "what_is_happening",
        "positive_factors",
        "negative_factors",
        "risks",
        "signals_to_watch",
        "portfolio_impact",
        "data_quality_notes",
        "questions_for_investor",
        "limitations",
        "not_financial_advice",
    ],
    "properties": {
        "schema_version": {"const": "1.0.0"},
        "prompt_version": {"type": "string"},
        "analysis_type": {"const": "instrument_context_analysis"},
        "ticker": {"type": "string"},
        "generated_at": {"type": "string", "format": "date-time"},
        "language": {"type": "string"},
        "executive_summary": {
            "type": "object",
            "required": ["title", "summary", "confidence"],
            "properties": {
                "title": {"type": "string"},
                "summary": {"type": "string"},
                "confidence": BASE_DEFINITIONS["confidence"],
            },
        },
        "what_is_happening": {"type": "array"},
        "positive_factors": {"type": "array"},
        "negative_factors": {"type": "array"},
        "risks": {"type": "array"},
        "signals_to_watch": {"type": "array"},
        "portfolio_impact": {"type": "object"},
        "data_quality_notes": {"type": "array"},
        "questions_for_investor": {"type": "array", "items": {"type": "string"}},
        "limitations": {"type": "array", "items": {"type": "string"}},
        "not_financial_advice": {"const": True},
    },
}


PORTFOLIO_CONTEXT_ANALYSIS_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "portfolio_context_analysis",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "prompt_version",
        "analysis_type",
        "portfolio_id",
        "generated_at",
        "language",
        "executive_summary",
        "portfolio_state",
        "risk_review",
        "opportunities_to_review",
        "alerts_to_prioritize",
        "forecast_context",
        "recommended_next_checks",
        "limitations",
        "not_financial_advice",
    ],
    "properties": {
        "schema_version": {"const": "1.0.0"},
        "prompt_version": {"type": "string"},
        "analysis_type": {"const": "portfolio_context_analysis"},
        "portfolio_id": {"type": "string"},
        "generated_at": {"type": "string", "format": "date-time"},
        "language": {"type": "string"},
        "executive_summary": {"type": "object"},
        "portfolio_state": {"type": "object"},
        "risk_review": {"type": "object"},
        "opportunities_to_review": {"type": "array"},
        "alerts_to_prioritize": {"type": "array"},
        "forecast_context": {"type": "object"},
        "recommended_next_checks": {"type": "array", "items": {"type": "string"}},
        "limitations": {"type": "array", "items": {"type": "string"}},
        "not_financial_advice": {"const": True},
    },
}


SCHEMAS: dict[str, dict[str, Any]] = {
    "instrument_context_analysis": INSTRUMENT_CONTEXT_ANALYSIS_SCHEMA,
    "portfolio_context_analysis": PORTFOLIO_CONTEXT_ANALYSIS_SCHEMA,
    "news_impact_analysis": PORTFOLIO_CONTEXT_ANALYSIS_SCHEMA,
    "dividend_strategy_analysis": PORTFOLIO_CONTEXT_ANALYSIS_SCHEMA,
    "risk_review": PORTFOLIO_CONTEXT_ANALYSIS_SCHEMA,
    "forecast_explanation": PORTFOLIO_CONTEXT_ANALYSIS_SCHEMA,
    "daily_market_briefing": PORTFOLIO_CONTEXT_ANALYSIS_SCHEMA,
    "alert_explanation": PORTFOLIO_CONTEXT_ANALYSIS_SCHEMA,
    "investment_thesis_review": INSTRUMENT_CONTEXT_ANALYSIS_SCHEMA,
}


def get_schema(schema_id: str) -> dict[str, Any]:
    return SCHEMAS[schema_id]
