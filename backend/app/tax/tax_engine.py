from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DISCLAIMER = (
    "Esta estimacion fiscal es orientativa y puede estar incompleta o desactualizada. "
    "No sustituye asesoramiento fiscal profesional."
)


class TaxEngine:
    def __init__(self, rules_dir: Path | None = None) -> None:
        self.rules_dir = rules_dir or Path(__file__).resolve().parent / "rules"

    def load_rules(self, country: str | None = None) -> list[dict[str, Any]]:
        files = [self.rules_dir / f"{country}.yml"] if country else sorted(self.rules_dir.glob("*.yml"))
        output: list[dict[str, Any]] = []
        for file in files:
            if not file.exists():
                continue
            data = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
            output.extend(data.get("rules", []))
        return output

    def estimate(self, payload: dict[str, Any]) -> dict[str, Any]:
        residence = str(payload.get("residence_country", "generic")).upper()
        rules = self.load_rules(residence) or self.load_rules("generic")
        dividends = float(payload.get("dividends", 0) or 0)
        gains = float(payload.get("capital_gains", 0) or 0)
        source_withholding = float(payload.get("source_withholding", 0.15) or 0.0)
        destination_rate = float(rules[0].get("rate", 0.19)) if rules else 0.19
        source_tax = dividends * source_withholding
        destination_tax = max(0.0, dividends * destination_rate - source_tax) + max(
            0.0, gains * destination_rate
        )
        return {
            "residence_country": residence,
            "source_country": payload.get("source_country", "US"),
            "gross_dividends": round(dividends, 2),
            "capital_gains": round(gains, 2),
            "source_tax": round(source_tax, 2),
            "destination_tax_estimate": round(destination_tax, 2),
            "net_after_estimated_tax": round(dividends + gains - source_tax - destination_tax, 2),
            "rules": rules,
            "confidence": min((rule.get("confidence", 0.5) for rule in rules), default=0.5),
            "disclaimer": DISCLAIMER,
        }
