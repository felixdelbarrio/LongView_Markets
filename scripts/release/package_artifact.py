from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if __name__ == "__main__":
    raise SystemExit(
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "package" / "build_release.py")],
            check=False,
        ).returncode
    )
