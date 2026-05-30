from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = [
    re.compile(r"gho_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]
EXCLUDED = {".git", ".venv", "node_modules", "dist", "data"}


def main() -> int:
    offenders: list[str] = []
    for path in ROOT.rglob("*"):
        if any(part in EXCLUDED for part in path.parts):
            continue
        if not path.is_file() or path.suffix in {".png", ".ico", ".icns"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(pattern.search(text) for pattern in PATTERNS):
            offenders.append(str(path.relative_to(ROOT)))
    if offenders:
        print("Potential secrets found:")
        for offender in offenders:
            print(f"- {offender}")
        return 1
    print("No obvious secrets found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
