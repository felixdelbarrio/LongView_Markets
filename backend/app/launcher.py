from __future__ import annotations

import os
import signal
import subprocess  # nosec B404
import sys
import time
import webbrowser
from pathlib import Path

from app.repositories.demo_repository import ensure_demo_files


def find_project_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2])).resolve()


def main() -> int:
    root = find_project_root()
    ensure_demo_files(root)
    port = os.environ.get("LONGVIEW_PORT", "8765")
    if not port.isdigit():
        raise ValueError("LONGVIEW_PORT must be numeric")
    # Static trusted local launcher command; shell is disabled and the port is validated.
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", port],
        cwd=root / "backend",
    )  # nosec B603
    url = f"http://127.0.0.1:{port}"
    print("LongView Markets packaged launcher")
    print(f"App URL: {url}")
    webbrowser.open(url)
    try:
        while process.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        process.send_signal(signal.SIGTERM)
    return process.wait()


if __name__ == "__main__":
    raise SystemExit(main())
