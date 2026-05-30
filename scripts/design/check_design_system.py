from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / "frontend" / "src" / "pages"
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}")


def main() -> int:
    errors: list[str] = []
    for path in PAGES.glob("*.tsx"):
        text = path.read_text(encoding="utf-8")
        if "style={{" in text:
            errors.append(f"{path.relative_to(ROOT)} uses inline style")
        if HEX_COLOR.search(text):
            errors.append(f"{path.relative_to(ROOT)} hardcodes a hex color")
    if errors:
        print("Design-system violations:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Design-system checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
