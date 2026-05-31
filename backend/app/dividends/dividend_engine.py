from __future__ import annotations

from datetime import date
from typing import Any


class DividendEngine:
    warning = (
        "Capturar dividendos no implica beneficio automatico. El precio suele ajustarse el dia "
        "ex-dividend aproximadamente por el importe del dividendo, y pueden existir impuestos, "
        "comisiones, spreads y riesgo de mercado."
    )

    def calendar(self, dividends: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(dividends, key=lambda item: item["ex_dividend_date"])

    def opportunities(
        self, dividends: list[dict[str, Any]], latest_prices: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        today = date.today()
        for dividend in dividends:
            ticker = dividend["ticker"]
            price = latest_prices.get(ticker, {}).get("close", 0) or 0
            ex_date = date.fromisoformat(dividend["ex_dividend_date"])
            gross_yield = float(dividend["amount"]) / float(price) if price else 0
            rows.append(
                {
                    **dividend,
                    "days_to_ex_dividend": (ex_date - today).days,
                    "estimated_gross_yield": round(gross_yield * 100, 2),
                    "estimated_net_yield": round(gross_yield * 0.79 * 100, 2),
                    "cut_risk": "medium" if gross_yield > 0.04 else "low",
                    "warning": self.warning,
                }
            )
        return sorted(rows, key=lambda item: item["days_to_ex_dividend"])[:20]
