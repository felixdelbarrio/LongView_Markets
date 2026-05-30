from __future__ import annotations

import math
from statistics import mean, pstdev
from typing import Any

METRIC_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "current_price": {
        "label": "Current reference price",
        "meaning": "Latest close in the local analytical lake.",
        "calculation": "Last adjusted close from daily prices.",
        "limitations": "Demo data may not reflect live markets.",
    },
    "cagr": {
        "label": "CAGR",
        "meaning": "Annualized growth over the available period.",
        "calculation": "(ending / beginning) ** (1 / years) - 1.",
        "limitations": "Sensitive to start and end dates.",
    },
    "volatility": {
        "label": "Volatility",
        "meaning": "Annualized dispersion of daily returns.",
        "calculation": "Population standard deviation of daily returns multiplied by sqrt(252).",
        "limitations": "Backward-looking and unstable during regime shifts.",
    },
    "max_drawdown": {
        "label": "Max drawdown",
        "meaning": "Largest peak-to-trough decline.",
        "calculation": "Minimum value of close / running peak - 1.",
        "limitations": "Does not describe recovery probability.",
    },
    "sharpe": {
        "label": "Simplified Sharpe",
        "meaning": "Return per unit of volatility before fees and taxes.",
        "calculation": "Mean daily return / daily volatility * sqrt(252).",
        "limitations": "Uses zero risk-free rate in v1.",
    },
    "dividend_yield": {
        "label": "Dividend yield",
        "meaning": "Forward dividend income estimate versus price.",
        "calculation": "Next four demo dividends / current price.",
        "limitations": "Dividend continuity is not guaranteed.",
    },
}


def pct(value: float) -> float:
    return round(value * 100, 2)


def moving_average(values: list[float], window: int) -> float | None:
    if len(values) < window:
        return None
    return round(mean(values[-window:]), 4)


def daily_returns(closes: list[float]) -> list[float]:
    return [
        (closes[index] / closes[index - 1]) - 1 for index in range(1, len(closes)) if closes[index - 1] != 0
    ]


def drawdowns(closes: list[float]) -> list[float]:
    peak = closes[0]
    output: list[float] = []
    for close in closes:
        peak = max(peak, close)
        output.append(close / peak - 1 if peak else 0)
    return output


class CalculationEngine:
    def calculate_price_metrics(
        self,
        prices: list[dict[str, Any]],
        benchmark_prices: list[dict[str, Any]] | None = None,
        dividends: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if len(prices) < 2:
            return {
                "status": "insufficient_data",
                "metrics": {},
                "descriptions": METRIC_DESCRIPTIONS,
            }
        closes = [float(row["adjusted_close"]) for row in prices]
        returns = daily_returns(closes)
        years = max((len(closes) - 1) / 252, 1 / 252)
        start = closes[0]
        end = closes[-1]
        current_year = str(prices[-1]["date"])[:4]
        ytd_start = next(
            (float(row["adjusted_close"]) for row in prices if str(row["date"]).startswith(current_year)),
            start,
        )
        dds = drawdowns(closes)
        volatility = pstdev(returns) * math.sqrt(252) if len(returns) > 1 else 0.0
        average_return = mean(returns) if returns else 0.0
        sharpe = (
            average_return / pstdev(returns) * math.sqrt(252) if len(returns) > 1 and pstdev(returns) else 0.0
        )
        ma20 = moving_average(closes, 20)
        ma50 = moving_average(closes, 50)
        ma200 = moving_average(closes, 200)
        benchmark_strength = 0.0
        if benchmark_prices and len(benchmark_prices) > 2:
            benchmark_closes = [float(row["adjusted_close"]) for row in benchmark_prices[-len(closes) :]]
            benchmark_strength = (end / start - 1) - (benchmark_closes[-1] / benchmark_closes[0] - 1)
        dividend_amount = sum(float(row["amount"]) for row in (dividends or [])[:4])
        trend = (
            "uptrend"
            if ma50 and ma200 and ma50 > ma200
            else "watch" if ma50 and ma200 else "insufficient_history"
        )
        cross = "bullish_50_200" if ma50 and ma200 and ma50 > ma200 else "bearish_or_neutral"
        metrics = {
            "current_price": round(end, 2),
            "daily_return": pct(end / closes[-2] - 1),
            "cumulative_return": pct(end / start - 1),
            "ytd_return": pct(end / ytd_start - 1),
            "cagr": pct((end / start) ** (1 / years) - 1),
            "volatility": pct(volatility),
            "max_drawdown": pct(min(dds)),
            "current_drawdown": pct(dds[-1]),
            "sharpe": round(sharpe, 2),
            "moving_average_20": ma20,
            "moving_average_50": ma50,
            "moving_average_200": ma200,
            "moving_average_cross": cross,
            "trend": trend,
            "relative_strength_vs_benchmark": pct(benchmark_strength),
            "total_return": pct((end + dividend_amount) / start - 1),
            "dividend_yield": pct(dividend_amount / end) if end else 0.0,
        }
        return {
            "status": "ok",
            "metrics": metrics,
            "descriptions": METRIC_DESCRIPTIONS,
            "lineage": {
                "source": "LongView deterministic seed",
                "as_of": prices[-1]["ingested_at"],
                "confidence": prices[-1].get("confidence", 0.8),
                "data_kind": prices[-1].get("data_kind", "mock"),
            },
        }

    def calculate_portfolio_metrics(
        self,
        transactions: list[dict[str, Any]],
        latest_prices: dict[str, dict[str, Any]],
        instruments: list[dict[str, Any]],
    ) -> dict[str, Any]:
        by_ticker: dict[str, dict[str, Any]] = {}
        instrument_map = {item["ticker"]: item for item in instruments}
        for transaction in transactions:
            row = by_ticker.setdefault(transaction["ticker"], {"quantity": 0.0, "cost": 0.0, "fees": 0.0})
            sign = 1 if transaction["transaction_type"] == "buy" else -1
            row["quantity"] += sign * float(transaction["quantity"])
            row["cost"] += sign * float(transaction["quantity"]) * float(transaction["price"])
            row["fees"] += float(transaction.get("fees", 0))
        positions: list[dict[str, Any]] = []
        total_value = 0.0
        total_cost = 0.0
        for ticker, row in by_ticker.items():
            latest = latest_prices[ticker]
            value = row["quantity"] * float(latest["close"])
            total_value += value
            total_cost += row["cost"] + row["fees"]
            instrument = instrument_map.get(ticker, {})
            positions.append(
                {
                    "ticker": ticker,
                    "quantity": round(row["quantity"], 4),
                    "market_value": round(value, 2),
                    "cost_basis": round(row["cost"] + row["fees"], 2),
                    "unrealized_return": (pct(value / (row["cost"] + row["fees"]) - 1) if row["cost"] else 0),
                    "sector": instrument.get("sector", "Unknown"),
                    "country": instrument.get("country", "Unknown"),
                    "currency": instrument.get("currency", latest.get("currency", "USD")),
                }
            )
        for position in positions:
            position["weight"] = pct(position["market_value"] / total_value) if total_value else 0.0
        top5 = sum(sorted((position["market_value"] for position in positions), reverse=True)[:5])
        return {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "unrealized_return": pct(total_value / total_cost - 1) if total_cost else 0,
            "net_estimated_return": (pct((total_value - total_cost) / total_cost) if total_cost else 0),
            "top5_concentration": pct(top5 / total_value) if total_value else 0,
            "positions": positions,
        }
