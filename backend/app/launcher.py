from __future__ import annotations

import os
import sys
import threading
import time
from http.client import HTTPConnection
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from app.db.database import ensure_database

APP_TITLE = "LongView Markets"


def find_project_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2])).resolve()


def runtime_cwd(root: Path) -> Path:
    backend = root / "backend"
    return backend if backend.exists() else root


def ensure_local_runtime(root: Path) -> None:
    os.environ.setdefault("LONGVIEW_PROJECT_ROOT", str(root))
    os.environ.setdefault("LONGVIEW_FRONTEND_DIST", str(root / "frontend_dist"))
    env = root / ".env"
    env_example = root / ".env.example"
    if not env.exists() and env_example.exists():
        env.write_text(env_example.read_text(encoding="utf-8"), encoding="utf-8")
    ensure_database(root / "data" / "longview.sqlite")


def start_backend(root: Path, port: str) -> tuple[Any, threading.Thread]:
    import uvicorn

    ensure_local_runtime(root)
    config = uvicorn.Config(
        "app.main:app",
        host="127.0.0.1",
        port=int(port),
        log_level="info",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="longview-markets-backend", daemon=True)
    thread.start()
    return server, thread


def wait_for_backend(url: str, timeout: float = 20) -> None:
    parsed = urlparse(url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or int(os.environ.get("LONGVIEW_PORT", "8765"))
    deadline = time.time() + timeout
    while time.time() < deadline:
        connection: HTTPConnection | None = None
        try:
            connection = HTTPConnection(host, port, timeout=1)
            connection.request("GET", "/api/v1/health")
            response = connection.getresponse()
            try:
                if response.status < 500:
                    return
            finally:
                response.close()
        except OSError:
            time.sleep(0.25)
        finally:
            if connection is not None:
                connection.close()
    raise RuntimeError("LongView Markets backend did not become ready in time")


def stop_backend(server: Any, thread: threading.Thread) -> None:
    server.should_exit = True
    thread.join(timeout=10)


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
    port = os.environ.get("LONGVIEW_PORT", "8765")
    if not port.isdigit():
        raise ValueError("LONGVIEW_PORT must be numeric")
    url = f"http://127.0.0.1:{port}"
    print("LongView Markets packaged launcher")
    print(f"Runtime root: {runtime_cwd(root)}")
    print("Opening native app frame")
    print(f"Internal URL: {url}")
    server, thread = start_backend(root, port)
    try:
        wait_for_backend(url)
        return open_app_frame(root, url)
    except KeyboardInterrupt:
        return 130
    finally:
        stop_backend(server, thread)


if __name__ == "__main__":
    raise SystemExit(main())
