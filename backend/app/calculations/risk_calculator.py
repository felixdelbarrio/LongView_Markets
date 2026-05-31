from __future__ import annotations


def concentration_flag(weight: float) -> str:
    return "position_weight_high" if weight >= 35 else "risk_controlled"
