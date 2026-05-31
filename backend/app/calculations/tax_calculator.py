from __future__ import annotations


def net_after_tax(amount: float, tax: float = 0.0) -> float:
    return round(amount - tax, 4)
