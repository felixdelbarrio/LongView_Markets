from __future__ import annotations

from app.analytics.calculation_engine import METRIC_DESCRIPTIONS


def explain_metric(metric: str) -> dict[str, str]:
    return METRIC_DESCRIPTIONS.get(
        metric,
        {
            "label": metric,
            "meaning": "LongView calculated metric.",
            "calculation": "Calculated in the backend calculation engine.",
            "limitations": "Review source, date and confidence before using it.",
        },
    )
