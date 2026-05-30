from __future__ import annotations


def sentiment_score(label: str) -> float:
    return {"positive": 0.65, "neutral": 0.5, "negative": 0.35}.get(label, 0.5)
