from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest

TEST_PROJECT_ROOT = Path(tempfile.mkdtemp(prefix="longview-tests-")).resolve()
SOURCE_APP_ROOT = Path(__file__).resolve().parents[1]
SOURCE_UNIVERSES = SOURCE_APP_ROOT / "data" / "universes"
TARGET_UNIVERSES = TEST_PROJECT_ROOT / "backend" / "app" / "data" / "universes"

TARGET_UNIVERSES.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(SOURCE_UNIVERSES, TARGET_UNIVERSES, dirs_exist_ok=True)
(TEST_PROJECT_ROOT / "VERSION").write_text("0.1.0", encoding="utf-8")

os.environ["LONGVIEW_PROJECT_ROOT"] = str(TEST_PROJECT_ROOT)
os.environ["DEMO_MODE_ENABLED"] = "false"
os.environ["MOCK_FALLBACK_ENABLED"] = "false"


@pytest.fixture(autouse=True)
def reset_runtime_data() -> None:
    from app.core.config import get_settings
    from app.db.database import ensure_database

    data_dir = TEST_PROJECT_ROOT / "data"
    if data_dir.exists():
        shutil.rmtree(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    get_settings.cache_clear()
    ensure_database(get_settings().database_path)
