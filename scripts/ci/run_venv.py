from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENV = ROOT / ".venv"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python scripts/ci/run_venv.py <script-or-module> [args...]"
        )
    command = [str(venv_python()), *sys.argv[1:]]
    return subprocess.run(command, cwd=ROOT).returncode


if __name__ == "__main__":
    raise SystemExit(main())
