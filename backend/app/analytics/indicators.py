from __future__ import annotations

from app.analytics.calculation_engine import moving_average


def moving_average_signal(values: list[float]) -> str:
    ma50 = moving_average(values, 50)
    ma200 = moving_average(values, 200)
    if ma50 is None or ma200 is None:
        return "insufficient_history"
    return "bullish" if ma50 > ma200 else "bearish_or_neutral"
