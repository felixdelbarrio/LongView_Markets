from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import Any

from app.calculations.fx_calculator import FxCalculator
from app.calculations.portfolio_calculator import PortfolioCalculator

CALCULATION_ENGINE_VERSION = "0.2.0"


class OperationalCalculationEngine:
    def __init__(self, base_currency: str = "EUR") -> None:
        self.base_currency = base_currency
        self.portfolio_calculator = PortfolioCalculator(base_currency)
        self.fx_calculator = FxCalculator(base_currency)

    def portfolio_valuation(
        self,
        transactions: list[dict[str, Any]],
        latest_prices: dict[str, dict[str, Any]],
        instruments: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self.portfolio_calculator.value(transactions, latest_prices, instruments)

    def portfolio_history(
        self,
        transactions: list[dict[str, Any]],
        prices_by_ticker: dict[str, list[dict[str, Any]]],
        instruments: list[dict[str, Any]],
        start: date | None = None,
        end: date | None = None,
    ) -> dict[str, Any]:
        rows = self.portfolio_calculator.history(transactions, prices_by_ticker, instruments, start, end)
        return {
            "portfolio_id": "real",
            "currency": self.base_currency,
            "history": rows,
            "calculation_version": CALCULATION_ENGINE_VERSION,
            "calculated_at": datetime.now(UTC).isoformat(),
            "inputs_summary": {"transactions": len(transactions), "days": len(rows)},
            "data_sources": ["sqlite", "parquet_prices", "fx_cache"],
            "warnings": [],
            "quality_flags": sorted({flag for row in rows for flag in row.get("data_quality_flags", [])}),
        }

    def instrument_history(
        self,
        ticker: str,
        transactions: list[dict[str, Any]],
        prices_by_ticker: dict[str, list[dict[str, Any]]],
        instruments: list[dict[str, Any]],
        start: date | None = None,
        end: date | None = None,
    ) -> dict[str, Any]:
        rows = self.portfolio_calculator.instrument_history(
            ticker, transactions, prices_by_ticker, instruments, start, end
        )
        return {
            "ticker": ticker.upper(),
            "portfolio_id": "real",
            "currency": self.base_currency,
            "history": rows,
            "calculation_version": CALCULATION_ENGINE_VERSION,
            "calculated_at": datetime.now(UTC).isoformat(),
            "inputs_summary": {"transactions": len(transactions), "days": len(rows)},
            "data_sources": ["sqlite", "parquet_prices", "fx_cache"],
            "warnings": [],
            "quality_flags": sorted({flag for row in rows for flag in row.get("data_quality_flags", [])}),
        }

    def fx_conversion(self, amount: float, from_currency: str, on_date: date | None = None) -> dict[str, Any]:
        converted = self.fx_calculator.convert(amount, from_currency, on_date)
        return {
            "amount": amount,
            "from_currency": from_currency.upper(),
            "to_currency": self.base_currency,
            "converted_amount": converted["converted"],
            "fx_rate": converted["rate"],
            "fx_rate_date": converted["date"],
            "data_kind": converted["data_kind"],
            "calculation_version": CALCULATION_ENGINE_VERSION,
            "calculated_at": datetime.now(UTC).isoformat(),
            "inputs_summary": {"amount": amount, "from_currency": from_currency},
            "data_sources": [str(converted["provider"])],
            "warnings": [],
            "quality_flags": [str(converted["quality_flag"])],
        }

    def forecast_instrument(
        self, ticker: str, prices: list[dict[str, Any]], horizon_days: int = 180
    ) -> dict[str, Any]:
        last = float((prices[-1] if prices else {"adjusted_close": 100}).get("adjusted_close", 100))
        generated_at = datetime.now(UTC)
        scenarios: list[dict[str, Any]] = []
        for name, multiplier in [
            ("adverso", 0.88),
            ("central", 1.04),
            ("optimista", 1.16),
        ]:
            scenarios.append(
                {
                    "scenario": name,
                    "date": (generated_at.date() + timedelta(days=horizon_days)).isoformat(),
                    "expected_price": round(last * multiplier, 2),
                    "confidence_low": round(last * (multiplier - 0.08), 2),
                    "confidence_high": round(last * (multiplier + 0.08), 2),
                    "expected_return": round((multiplier - 1) * 100, 2),
                    "risk_flags": ["forecast_uncertainty"],
                }
            )
        return {
            "entity_type": "instrument",
            "entity_id": ticker.upper(),
            "ticker": ticker.upper(),
            "generated_at": generated_at.isoformat(),
            "model_name": "longview_prudent_scenario",
            "model_version": "0.2.0",
            "horizon_days": horizon_days,
            "scenarios": scenarios,
            "confidence": 0.62,
            "features_used": [
                "daily_return",
                "volatility_20d",
                "drawdown",
                "news_sentiment_score",
            ],
            "limitations": [
                "Escenarios informativos, no predicciones garantizadas.",
                "Datos gratuitos pueden tener retrasos.",
            ],
            "data_quality_flags": ["forecast_uncertainty"],
            "generative_context_used": False,
            "calculation_version": CALCULATION_ENGINE_VERSION,
            "calculated_at": generated_at.isoformat(),
            "inputs_summary": {"price_rows": len(prices)},
            "data_sources": ["parquet_prices"],
            "warnings": [],
            "quality_flags": ["forecast_uncertainty"],
        }

    def forecast_portfolio(self, valuation: dict[str, Any], horizon_days: int = 180) -> dict[str, Any]:
        base = float(valuation.get("total_market_value_base", 0))
        generated_at = datetime.now(UTC)
        scenarios = [
            {
                "date": (generated_at.date() + timedelta(days=horizon_days)).isoformat(),
                "scenario": name,
                "market_value_base": round(base * multiplier, 2),
                "confidence_low": round(base * (multiplier - 0.06), 2),
                "confidence_high": round(base * (multiplier + 0.06), 2),
                "expected_return": round((multiplier - 1) * 100, 2),
                "expected_drawdown": drawdown,
                "risk_flags": valuation.get("risk_flags", []),
                "generative_context_used": False,
            }
            for name, multiplier, drawdown in [
                ("adverso", 0.9, -16),
                ("central", 1.035, -8),
                ("optimista", 1.12, -5),
            ]
        ]
        return {
            "entity_type": "portfolio",
            "entity_id": valuation.get("portfolio_id", "real"),
            "generated_at": generated_at.isoformat(),
            "model_name": "longview_portfolio_scenario",
            "model_version": "0.2.0",
            "horizon_days": horizon_days,
            "scenarios": scenarios,
            "confidence": 0.6,
            "features_used": [
                "portfolio_daily_return",
                "concentration_top_5",
                "currency_exposure",
            ],
            "limitations": [
                "No incorpora eventos corporativos futuros no observados.",
                "No es asesoramiento financiero.",
            ],
            "data_quality_flags": ["forecast_uncertainty"],
            "generative_context_used": False,
            "calculation_version": CALCULATION_ENGINE_VERSION,
            "calculated_at": generated_at.isoformat(),
            "inputs_summary": {"positions": len(valuation.get("positions", []))},
            "data_sources": ["calculation_engine"],
            "warnings": [],
            "quality_flags": ["forecast_uncertainty"],
        }
