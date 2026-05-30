from __future__ import annotations

import os
import signal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PID_DIR = ROOT / ".pids"


def main() -> int:
    if not PID_DIR.exists():
        print("No LongView Markets PID files found.")
        return 0
    stopped = 0
    for file in PID_DIR.glob("*.pid"):
        try:
            pid = int(file.read_text().strip())
            try:
                os.killpg(pid, signal.SIGTERM)
            except ProcessLookupError:
                os.kill(pid, signal.SIGTERM)
            stopped += 1
            print(f"Stopped {file.stem} ({pid})")
        except (OSError, ValueError):
            print(f"{file.stem} was not running")
        file.unlink(missing_ok=True)
    return 0 if stopped >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
