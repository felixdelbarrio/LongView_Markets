from __future__ import annotations


def simulate_capture(
    price: float, dividend: float, tax_rate: float = 0.19, fees: float = 2.0
) -> dict[str, float]:
    gross = dividend
    net = dividend * (1 - tax_rate) - fees
    adjusted_exit = price - dividend
    return {
        "buy_price": round(price, 2),
        "expected_ex_dividend_price": round(adjusted_exit, 2),
        "gross_dividend": round(gross, 2),
        "net_dividend_after_tax_and_fees": round(net, 2),
        "central_result": round(adjusted_exit + net - price, 2),
    }
