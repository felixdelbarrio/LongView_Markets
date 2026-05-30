from __future__ import annotations


def concentration_status(top5_weight: float) -> str:
    if top5_weight >= 75:
        return "high"
    if top5_weight >= 55:
        return "medium"
    return "controlled"
