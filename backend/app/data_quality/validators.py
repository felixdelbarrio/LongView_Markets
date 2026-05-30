from __future__ import annotations

from typing import Any


def validate_ohlc(row: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if row["close"] <= 0 or row["open"] <= 0:
        warnings.append("non_positive_price")
    if row["high"] < max(row["open"], row["close"]):
        warnings.append("high_below_open_or_close")
    if row["low"] > min(row["open"], row["close"]):
        warnings.append("low_above_open_or_close")
    if row["volume"] < 0:
        warnings.append("negative_volume")
    return warnings
