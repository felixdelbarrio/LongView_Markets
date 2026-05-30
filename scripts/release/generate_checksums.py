from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist", nargs="?", default="dist")
    args = parser.parse_args()
    dist = Path(args.dist)
    files = sorted([*dist.glob("*.zip"), *dist.glob("*.tar.gz")])
    lines = [
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}"
        for path in files
    ]
    (dist / "checksums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {dist / 'checksums.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
