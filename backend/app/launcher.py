from __future__ import annotations

import os
import signal
import subprocess  # nosec B404
import sys
import time
from pathlib import Path

from app.repositories.demo_repository import ensure_demo_files

APP_TITLE = "LongView Markets"


def find_project_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2])).resolve()


def open_app_frame(root: Path, url: str) -> int:
    try:
        import webview
    except ImportError:
        print("LongView Markets requires pywebview in the packaged Python runtime.")
        return 1

    icon = root / "assets" / "longview-icon.png"
    webview.create_window(
        title=APP_TITLE,
        url=url,
        width=1440,
        height=920,
        min_size=(1120, 760),
        text_select=True,
    )
    webview.start(icon=str(icon) if icon.exists() else None)
    return 0


def main() -> int:
    root = find_project_root()
    ensure_demo_files(root)
    port = os.environ.get("LONGVIEW_PORT", "8765")
    if not port.isdigit():
        raise ValueError("LONGVIEW_PORT must be numeric")
    # Static trusted local launcher command; shell is disabled and the port is validated.
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            port,
        ],
        cwd=root / "backend",
    )  # nosec B603
    url = f"http://127.0.0.1:{port}"
    print("LongView Markets packaged launcher")
    print("Opening native app frame")
    print(f"Internal URL: {url}")
    try:
        time.sleep(1)
        return open_app_frame(root, url)
    except KeyboardInterrupt:
        process.send_signal(signal.SIGTERM)
        return process.wait()
    finally:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)


if __name__ == "__main__":
    raise SystemExit(main())
