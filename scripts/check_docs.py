from __future__ import annotations

from pathlib import Path

REQUIRED = [
    "architecture.md",
    "product-principles.md",
    "data-model.md",
    "providers.md",
    "parquet.md",
    "analytics.md",
    "insights.md",
    "alerts.md",
    "portfolios.md",
    "simulated-portfolio.md",
    "dividends.md",
    "tax-advisor.md",
    "forecasting.md",
    "gpt-copilot.md",
    "i18n.md",
    "security.md",
    "testing.md",
    "release.md",
    "ci-cd.md",
    "branch-protection.md",
    "makefile.md",
    "data-quality.md",
    "screener.md",
    "watchlists.md",
    "decision-journal.md",
    "playbooks.md",
    "launcher.md",
    "branding.md",
    "limitations.md",
    "user-guide.md",
]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    missing = [name for name in REQUIRED if not (root / "docs" / name).exists()]
    readme = (
        (root / "README.md").read_text(encoding="utf-8")
        if (root / "README.md").exists()
        else ""
    )
    badges = [
        "backend-ci.yml",
        "frontend-ci.yml",
        "codeql.yml",
        "security.yml",
        "coverage.yml",
        "docs.yml",
        "release.yml",
    ]
    if missing or any(badge not in readme for badge in badges):
        print(f"Missing docs: {missing}")
        return 1
    print("Docs inventory ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
