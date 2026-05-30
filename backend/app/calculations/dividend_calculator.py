from __future__ import annotations


def net_dividend(gross: float, tax: float = 0.0) -> float:
    return round(gross - tax, 4)
