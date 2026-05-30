from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType

import pytest

from app.launcher import open_app_frame


def test_packaged_launcher_opens_webview_frame(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[tuple[str, dict[str, object]]] = []
    fake_webview = ModuleType("webview")

    def create_window(**kwargs: object) -> None:
        calls.append(("create_window", kwargs))

    def start(**kwargs: object) -> None:
        calls.append(("start", kwargs))

    fake_webview.create_window = create_window  # type: ignore[attr-defined]
    fake_webview.start = start  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "webview", fake_webview)

    assets = tmp_path / "assets"
    assets.mkdir()
    icon = assets / "longview-icon.png"
    icon.write_bytes(b"icon")

    assert open_app_frame(tmp_path, "http://127.0.0.1:8765") == 0
    assert calls == [
        (
            "create_window",
            {
                "title": "LongView Markets",
                "url": "http://127.0.0.1:8765",
                "width": 1440,
                "height": 920,
                "min_size": (1120, 760),
                "text_select": True,
            },
        ),
        ("start", {"icon": str(icon)}),
    ]
