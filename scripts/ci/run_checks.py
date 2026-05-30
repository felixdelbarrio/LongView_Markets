from __future__ import annotations

import os
import subprocess
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
    python = venv_python()
    run([str(python), "-m", "ruff", "check", "app"], cwd=ROOT / "backend")
    run([str(python), "-m", "black", "--check", "app"], cwd=ROOT / "backend")
    run([str(python), "scripts/design/check_design_system.py"])
    run(["npm", "--prefix", "frontend", "run", "lint"])
    run(["npm", "--prefix", "frontend", "run", "format:check"])
    run([str(python), "-m", "mypy", "app"], cwd=ROOT / "backend")
    run(["npm", "--prefix", "frontend", "run", "typecheck"])
    run([str(python), "-m", "pytest", "--no-cov"], cwd=ROOT / "backend")
    run(["npm", "--prefix", "frontend", "run", "test"])
    run([str(python), "-m", "pytest"], cwd=ROOT / "backend")
    run(
        [str(python), "-m", "bandit", "-r", "app", "-q", "-x", "app/tests"],
        cwd=ROOT / "backend",
    )
    run([str(python), "-m", "pip_audit", "--skip-editable"], cwd=ROOT / "backend")
    run(["npm", "--prefix", "frontend", "audit", "--audit-level=critical"])
    run([str(python), "scripts/check_secrets.py"])
    run([str(python), "-m", "ruff", "check", "app"], cwd=ROOT / "backend")
    run(["npm", "--prefix", "frontend", "run", "build"])
    run([str(python), "scripts/package/build_release.py"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
