from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PID_DIR = ROOT / ".pids"
LOG_DIR = ROOT / "logs"


def ensure_env() -> None:
    env = ROOT / ".env"
    if not env.exists():
        env.write_text((ROOT / ".env.example").read_text(encoding="utf-8"), encoding="utf-8")


def stop_existing() -> None:
    if not PID_DIR.exists():
        return
    for file in PID_DIR.glob("*.pid"):
        try:
            pid = int(file.read_text().strip())
            os.kill(pid, signal.SIGTERM)
        except (OSError, ValueError):
            pass
        file.unlink(missing_ok=True)


def start(name: str, command: list[str], cwd: Path) -> subprocess.Popen[bytes]:
    LOG_DIR.mkdir(exist_ok=True)
    log = open(LOG_DIR / f"{name}.log", "ab")
    process = subprocess.Popen(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    log.close()
    PID_DIR.mkdir(exist_ok=True)
    (PID_DIR / f"{name}.pid").write_text(str(process.pid), encoding="utf-8")
    return process


def main() -> int:
    ensure_env()
    stop_existing()
    backend_python = ROOT / ".venv" / "bin" / "python"
    if not backend_python.exists():
        print("Missing .venv. Run `make install` first.")
        return 1
    seed = subprocess.run(
        [str(backend_python), "-m", "app.cli.main", "--project-root", str(ROOT)],
        cwd=ROOT / "backend",
        check=False,
    )
    if seed.returncode != 0:
        return seed.returncode
    backend = start(
        "backend",
        [str(backend_python), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        ROOT / "backend",
    )
    frontend = start("frontend", ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"], ROOT / "frontend")
    time.sleep(2)
    if backend.poll() is not None or frontend.poll() is not None:
        print("LongView Markets failed to start. Check logs/backend.log and logs/frontend.log.")
        return 1
    print("")
    print("LongView Markets is running")
    print("Frontend: http://localhost:5173")
    print("Backend:  http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Demo user loaded")
    print("Seed data loaded")
    print("Parquet lake ready")
    print("SQLite metadata ready")
    print("Use `make kill` to stop LongView Markets.")
    print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
