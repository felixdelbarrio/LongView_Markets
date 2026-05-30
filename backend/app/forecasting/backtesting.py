from __future__ import annotations


def simple_directional_accuracy(expected: list[float], observed: list[float]) -> float:
    pairs = zip(expected[1:], expected[:-1], observed[1:], observed[:-1], strict=False)
    hits = [
        ((exp_now - exp_prev) >= 0) == ((obs_now - obs_prev) >= 0)
        for exp_now, exp_prev, obs_now, obs_prev in pairs
    ]
    return round(sum(hits) / len(hits), 4) if hits else 0.0
