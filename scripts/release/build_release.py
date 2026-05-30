from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(command: list[str], cwd: Path = ROOT) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def build_windows_exe() -> Path:
    icon = ROOT / "scripts" / "package" / "assets" / "longview-icon.ico"
    if platform.system() != "Windows":
        raise RuntimeError("Windows exe can only be built on a Windows runner")
    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--name",
            "LongView Markets",
            "--onefile",
            "--windowed",
            "--icon",
            str(icon),
            "--add-data",
            "frontend/dist;frontend_dist",
            "--add-data",
            ".env.example;.",
            "--add-data",
            "data/seed;data/seed",
            "--add-data",
            "backend/app/data;backend/app/data",
            "--add-data",
            "scripts/package/assets;assets",
            "--hidden-import",
            "app.main",
            "--hidden-import",
            "app.api.routes.router",
            "backend/app/launcher.py",
        ]
    )
    exe = ROOT / "dist" / "LongView Markets.exe"
    if not exe.exists() or exe.stat().st_size == 0:
        raise RuntimeError("PyInstaller did not produce LongView Markets.exe")
    return exe


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform", choices=["windows", "linux", "macos", "all"], default="all"
    )
    parser.add_argument("--with-pyinstaller", action="store_true")
    args = parser.parse_args()
    run(["npm", "--prefix", "frontend", "run", "build"])
    if args.with_pyinstaller and args.platform == "windows":
        build_windows_exe()
    run(
        [
            sys.executable,
            "scripts/package/build_release.py",
            "--platform",
            args.platform,
        ]
    )
    run([sys.executable, "scripts/release/generate_checksums.py"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
