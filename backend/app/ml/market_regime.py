from __future__ import annotations


class MarketRegime:
    def classify(self, drawdown: float, momentum: float) -> str:
        if drawdown < -0.15:
            return "stress"
        if momentum > 0.05:
            return "expansion"
        return "neutral"
