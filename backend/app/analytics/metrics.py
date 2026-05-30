from __future__ import annotations

from app.analytics.calculation_engine import METRIC_DESCRIPTIONS


def get_metric_catalog() -> dict[str, dict[str, str]]:
    return METRIC_DESCRIPTIONS
