from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VENV = ROOT / ".venv"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def run(command: list[str], cwd: Path = ROOT) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    if not VENV.exists():
        run([sys.executable, "-m", "venv", str(VENV)])
    python = venv_python()
    run([str(python), "-m", "pip", "install", "--upgrade", "pip"])
    run([str(python), "-m", "pip", "install", "-e", "backend[dev]"])
    run(["npm", "--prefix", "frontend", "install"])
    env = ROOT / ".env"
    if not env.exists():
        shutil.copy(ROOT / ".env.example", env)
    run(
        [str(python), "-m", "app.cli.main", "--project-root", ".."],
        cwd=ROOT / "backend",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
