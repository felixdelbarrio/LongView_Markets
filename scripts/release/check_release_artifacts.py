from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"


def _zip_names(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as bundle:
        return set(bundle.namelist())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", default="current")
    parser.add_argument("--allow-missing-windows-exe", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    if not (DIST / "checksums.txt").exists():
        errors.append("dist/checksums.txt missing")
    expected_archives = {
        "linux": ["LongView-Markets-linux.tar.gz"],
        "macos": ["LongView-Markets-macos.tar.gz"],
        "windows": ["LongView-Markets-windows.zip"],
        "current": [
            "LongView-Markets-linux.tar.gz",
            "LongView-Markets-macos.tar.gz",
            "LongView-Markets-windows.zip",
        ],
        "all": [
            "LongView-Markets-linux.tar.gz",
            "LongView-Markets-macos.tar.gz",
            "LongView-Markets-windows.zip",
        ],
    }.get(
        args.platform,
        [
            "LongView-Markets-linux.tar.gz",
            "LongView-Markets-macos.tar.gz",
            "LongView-Markets-windows.zip",
        ],
    )
    for archive in expected_archives:
        if not (DIST / archive).exists():
            errors.append(f"dist/{archive} missing")
    windows_zip = DIST / "LongView-Markets-windows.zip"
    if "LongView-Markets-windows.zip" not in expected_archives:
        windows_zip = Path("")
    elif not windows_zip.exists():
        errors.append("dist/LongView-Markets-windows.zip missing")
    elif windows_zip:
        names = _zip_names(windows_zip)
        has_env = any(name.endswith("/.env") or name == ".env" for name in names)
        has_env_example = any(name.endswith(".env.example") for name in names)
        has_readme = any(
            name.endswith("README-RUNTIME.md") or name.endswith("README.md")
            for name in names
        )
        has_exe = any(name.endswith("LongView Markets.exe") for name in names)
        if has_env:
            errors.append("Windows artifact packages .env")
        if not has_env_example:
            errors.append("Windows artifact missing .env.example")
        if not has_readme:
            errors.append("Windows artifact missing runtime README")
        if not has_exe and not args.allow_missing_windows_exe:
            errors.append("Windows artifact missing LongView Markets.exe")
    if errors:
        print("Release artifact validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Release artifact validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
