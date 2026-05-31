from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from typing import Any, cast

from app.calculations.fx_calculator import FxCalculator


def pct(numerator: float, denominator: float) -> float:
    return round((numerator / denominator * 100), 4) if denominator else 0.0


def parse_date(value: str | date | None) -> date:
    if value is None:
        raise ValueError("date value is required")
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def business_days(start: date, end: date) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


class PortfolioCalculator:
    def __init__(self, base_currency: str = "EUR") -> None:
        self.base_currency = base_currency
        self.fx = FxCalculator(base_currency)

    def _convert(self, amount: float, currency: str, on_date: date) -> tuple[float, dict[str, object]]:
        fx = self.fx.convert(amount, currency, on_date)
        return float(cast(float, fx["converted"])), fx

    def value(
        self,
        transactions: list[dict[str, Any]],
        latest_prices: dict[str, dict[str, Any]],
        instruments: list[dict[str, Any]],
    ) -> dict[str, Any]:
        instrument_map = {item["ticker"].upper(): item for item in instruments}
        lots: dict[str, list[dict[str, Any]]] = defaultdict(list)
        realized: dict[str, float] = defaultdict(float)
        dividends: dict[str, float] = defaultdict(float)
        fees: dict[str, float] = defaultdict(float)
        taxes: dict[str, float] = defaultdict(float)
        warnings: list[str] = []
        ordered = sorted(
            transactions,
            key=lambda row: (
                str(row.get("trade_date") or row.get("date")),
                str(row["id"]),
            ),
        )
        for row in ordered:
            ticker = str(row["ticker"]).upper()
            trade_date = parse_date(row.get("trade_date") or row.get("date"))
            currency = str(row.get("currency") or instrument_map.get(ticker, {}).get("currency", "EUR"))
            quantity = float(row.get("quantity") or 0)
            price = float(row.get("price") or 0)
            gross = float(row.get("gross_amount") or quantity * price)
            fee = float(row.get("fees") or 0)
            tax = float(row.get("taxes") or 0)
            fee_base, _ = self._convert(fee, currency, trade_date)
            tax_base, _ = self._convert(tax, currency, trade_date)
            fees[ticker] += fee_base
            taxes[ticker] += tax_base
            kind = str(row.get("transaction_type", "buy")).lower()
            if kind == "buy":
                cost_base, _ = self._convert(gross + fee + tax, currency, trade_date)
                lots[ticker].append(
                    {
                        "trade_date": trade_date.isoformat(),
                        "remaining_quantity": quantity,
                        "original_quantity": quantity,
                        "cost_base": cost_base,
                        "price": price,
                        "currency": currency,
                        "fees_base": fee_base,
                        "taxes_base": tax_base,
                    }
                )
            elif kind == "sell":
                proceeds_base, _ = self._convert(gross - fee - tax, currency, trade_date)
                remaining = quantity
                consumed_cost = 0.0
                for lot in lots[ticker]:
                    if remaining <= 0:
                        break
                    available = float(lot["remaining_quantity"])
                    take = min(available, remaining)
                    ratio = take / available if available else 0
                    consumed_cost += float(lot["cost_base"]) * ratio
                    lot["cost_base"] = float(lot["cost_base"]) * (1 - ratio)
                    lot["remaining_quantity"] = available - take
                    remaining -= take
                if remaining > 0:
                    warnings.append(f"negative_position_blocked:{ticker}")
                realized[ticker] += proceeds_base - consumed_cost
            elif kind == "dividend":
                amount_base, _ = self._convert(gross - tax, currency, trade_date)
                dividends[ticker] += amount_base
            elif kind in {"fee", "tax"}:
                continue
        positions: list[dict[str, Any]] = []
        total_market = 0.0
        total_invested = 0.0
        total_realized = 0.0
        total_dividends = 0.0
        total_fees = 0.0
        total_taxes = 0.0
        for ticker, ticker_lots in lots.items():
            open_lots = [lot for lot in ticker_lots if float(lot["remaining_quantity"]) > 1e-9]
            quantity = sum(float(lot["remaining_quantity"]) for lot in open_lots)
            if quantity <= 0:
                continue
            instrument = instrument_map.get(ticker, {"currency": "EUR", "name": ticker})
            latest = latest_prices.get(ticker) or {}
            market_price = float(latest.get("adjusted_close") or latest.get("close") or 0)
            price_date = parse_date(str(latest.get("date") or date.today().isoformat()))
            local_value = quantity * market_price
            market_base, fx = self._convert(local_value, str(instrument.get("currency", "EUR")), price_date)
            fx_rate = float(cast(float, fx["rate"]))
            invested = sum(float(lot["cost_base"]) for lot in open_lots)
            unrealized = market_base - invested
            total_market += market_base
            total_invested += invested
            total_realized += realized[ticker]
            total_dividends += dividends[ticker]
            total_fees += fees[ticker]
            total_taxes += taxes[ticker]
            positions.append(
                {
                    "ticker": ticker,
                    "name": instrument.get("name", ticker),
                    "quantity": round(quantity, 6),
                    "lots": open_lots,
                    "average_cost_local": (round((invested / fx_rate) / quantity, 4) if quantity else 0),
                    "average_cost_base": (round(invested / quantity, 4) if quantity else 0),
                    "invested_amount_local": (round(invested / fx_rate, 2) if fx_rate else invested),
                    "invested_amount_base": round(invested, 2),
                    "market_price_local": market_price,
                    "market_price_date": price_date.isoformat(),
                    "market_value_local": round(local_value, 2),
                    "market_value_base": round(market_base, 2),
                    "unrealized_pnl_local": (round(unrealized / fx_rate, 2) if fx_rate else unrealized),
                    "unrealized_pnl_base": round(unrealized, 2),
                    "unrealized_return_pct": pct(unrealized, invested),
                    "realized_pnl_base": round(realized[ticker], 2),
                    "dividends_received_base": round(dividends[ticker], 2),
                    "fees_paid_base": round(fees[ticker], 2),
                    "taxes_paid_base": round(taxes[ticker], 2),
                    "total_return_base": round(
                        unrealized + realized[ticker] + dividends[ticker] - fees[ticker] - taxes[ticker],
                        2,
                    ),
                    "total_return_pct": pct(unrealized + realized[ticker] + dividends[ticker], invested),
                    "currency": instrument.get("currency", "EUR"),
                    "base_currency": self.base_currency,
                    "fx_rate": fx_rate,
                    "fx_rate_date": fx["date"],
                    "sector": instrument.get("sector", "Unknown"),
                    "country": instrument.get("country", "Unknown"),
                    "data_quality_flags": [fx["quality_flag"]],
                    "calculation_version": "0.2.0",
                }
            )
        for position in positions:
            position["weight"] = pct(float(position["market_value_base"]), total_market)
        top_positions = sorted(positions, key=lambda row: float(row["market_value_base"]), reverse=True)
        return_base = (
            total_market - total_invested + total_realized + total_dividends - total_fees - total_taxes
        )
        return {
            "portfolio_id": "real",
            "base_currency": self.base_currency,
            "total_market_value_base": round(total_market, 2),
            "total_invested_base": round(total_invested, 2),
            "realized_pnl_base": round(total_realized, 2),
            "unrealized_pnl_base": round(total_market - total_invested, 2),
            "dividends_received_base": round(total_dividends, 2),
            "fees_paid_base": round(total_fees, 2),
            "taxes_paid_base": round(total_taxes, 2),
            "total_return_base": round(return_base, 2),
            "total_return_pct": pct(return_base, total_invested),
            "daily_change_base": 0.0,
            "daily_change_pct": 0.0,
            "ytd_return_pct": 0.0,
            "currency_exposure": self._exposure(positions, "currency"),
            "country_exposure": self._exposure(positions, "country"),
            "sector_exposure": self._exposure(positions, "sector"),
            "top_positions": top_positions[:5],
            "risk_flags": self._risk_flags(positions),
            "positions": positions,
            "calculation_version": "0.2.0",
            "calculated_at": datetime.now(UTC).isoformat(),
            "inputs_summary": {
                "transactions": len(transactions),
                "positions": len(positions),
            },
            "data_sources": ["sqlite", "parquet_prices", "fx_cache"],
            "warnings": warnings,
            "quality_flags": sorted(
                {flag for position in positions for flag in position["data_quality_flags"]}
            ),
        }

    def history(
        self,
        transactions: list[dict[str, Any]],
        prices_by_ticker: dict[str, list[dict[str, Any]]],
        instruments: list[dict[str, Any]],
        start: date | None = None,
        end: date | None = None,
    ) -> list[dict[str, Any]]:
        if not transactions:
            return []
        min_date = min(parse_date(row.get("trade_date") or row.get("date")) for row in transactions)
        max_price_date = max(
            (parse_date(row["date"]) for rows in prices_by_ticker.values() for row in rows),
            default=date.today(),
        )
        start_date = start or min_date
        end_date = end or max_price_date
        instrument_map = {item["ticker"].upper(): item for item in instruments}
        history: list[dict[str, Any]] = []
        previous_value = 0.0
        for current in business_days(start_date, end_date):
            active_transactions = [
                row for row in transactions if parse_date(row.get("trade_date") or row.get("date")) <= current
            ]
            latest_prices: dict[str, dict[str, Any]] = {}
            quality_flags: set[str] = set()
            for ticker, rows in prices_by_ticker.items():
                eligible = [row for row in rows if parse_date(row["date"]) <= current]
                if eligible:
                    latest_prices[ticker.upper()] = eligible[-1]
                    if parse_date(eligible[-1]["date"]) != current:
                        quality_flags.add("stale_price")
            valuation = self.value(active_transactions, latest_prices, instruments)
            cashflows = 0.0
            dividends = 0.0
            fees = 0.0
            taxes = 0.0
            for row in active_transactions:
                if parse_date(row.get("trade_date") or row.get("date")) != current:
                    continue
                currency = str(
                    row.get("currency")
                    or instrument_map.get(str(row["ticker"]).upper(), {}).get("currency", "EUR")
                )
                gross = float(
                    row.get("gross_amount") or float(row.get("quantity") or 0) * float(row.get("price") or 0)
                )
                converted, _ = self._convert(gross, currency, current)
                if row.get("transaction_type") == "buy":
                    cashflows += converted
                elif row.get("transaction_type") == "sell":
                    cashflows -= converted
                elif row.get("transaction_type") == "dividend":
                    dividends += converted
                fees += float(self._convert(float(row.get("fees") or 0), currency, current)[0])
                taxes += float(self._convert(float(row.get("taxes") or 0), currency, current)[0])
            value = float(valuation["total_market_value_base"])
            daily_pnl = value - previous_value - cashflows + dividends - fees - taxes if history else 0.0
            history.append(
                {
                    "date": current.isoformat(),
                    "market_value_base": round(value, 2),
                    "invested_capital_base": valuation["total_invested_base"],
                    "cashflows_base": round(cashflows, 2),
                    "dividends_base": round(dividends, 2),
                    "fees_base": round(fees, 2),
                    "taxes_base": round(taxes, 2),
                    "unrealized_pnl_base": valuation["unrealized_pnl_base"],
                    "realized_pnl_base": valuation["realized_pnl_base"],
                    "total_return_base": valuation["total_return_base"],
                    "total_return_pct": valuation["total_return_pct"],
                    "daily_pnl_base": round(daily_pnl, 2),
                    "daily_pnl_pct": (pct(daily_pnl, previous_value) if previous_value else 0.0),
                    "data_quality_flags": sorted(quality_flags | set(valuation["quality_flags"])),
                    "calculation_version": "0.2.0",
                }
            )
            previous_value = value
        return history

    def instrument_history(
        self,
        ticker: str,
        transactions: list[dict[str, Any]],
        prices_by_ticker: dict[str, list[dict[str, Any]]],
        instruments: list[dict[str, Any]],
        start: date | None = None,
        end: date | None = None,
    ) -> list[dict[str, Any]]:
        normalized = ticker.upper()
        rows = self.history(
            [row for row in transactions if str(row["ticker"]).upper() == normalized],
            {normalized: prices_by_ticker.get(normalized, [])},
            instruments,
            start,
            end,
        )
        output: list[dict[str, Any]] = []
        for row in rows:
            price_rows = [
                price for price in prices_by_ticker.get(normalized, []) if price["date"] <= row["date"]
            ]
            price = price_rows[-1] if price_rows else {}
            output.append(
                {
                    "date": row["date"],
                    "ticker": normalized,
                    "quantity": next(
                        (
                            position["quantity"]
                            for position in self.value(
                                [
                                    txn
                                    for txn in transactions
                                    if str(txn["ticker"]).upper() == normalized
                                    and parse_date(txn.get("trade_date") or txn.get("date"))
                                    <= parse_date(row["date"])
                                ],
                                {normalized: price},
                                instruments,
                            )["positions"]
                        ),
                        0,
                    ),
                    "market_price_local": price.get("adjusted_close") or price.get("close") or 0,
                    "market_value_local": row["market_value_base"],
                    "market_value_base": row["market_value_base"],
                    "invested_capital_base": row["invested_capital_base"],
                    "unrealized_pnl_base": row["unrealized_pnl_base"],
                    "realized_pnl_base": row["realized_pnl_base"],
                    "dividends_base": row["dividends_base"],
                    "daily_pnl_base": row["daily_pnl_base"],
                    "total_return_base": row["total_return_base"],
                    "total_return_pct": row["total_return_pct"],
                    "fx_rate": 1,
                    "data_quality_flags": row["data_quality_flags"],
                }
            )
        return output

    def _exposure(self, positions: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
        totals: dict[str, float] = defaultdict(float)
        total = sum(float(position["market_value_base"]) for position in positions)
        for position in positions:
            totals[str(position.get(key, "Unknown"))] += float(position["market_value_base"])
        return [
            {"name": name, "value_base": round(value, 2), "weight": pct(value, total)}
            for name, value in sorted(totals.items())
        ]

    def _risk_flags(self, positions: list[dict[str, Any]]) -> list[str]:
        flags: list[str] = []
        if any(float(position["weight"]) > 35 for position in positions):
            flags.append("position_weight_high")
        currency_weights = self._exposure(positions, "currency")
        if any(
            item["name"] != self.base_currency and float(item["weight"]) > 40 for item in currency_weights
        ):
            flags.append("currency_exposure_high")
        if not flags:
            flags.append("risk_controlled")
        return flags
