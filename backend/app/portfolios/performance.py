from __future__ import annotations


def benchmark_delta(portfolio_return: float, benchmark_return: float) -> float:
    return round(portfolio_return - benchmark_return, 2)
