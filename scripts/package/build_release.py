from __future__ import annotations

import hashlib
import shutil
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
DIST = ROOT / "dist"


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def stage_platform(platform: str) -> Path:
    target = DIST / f"LongView-Markets-{platform}"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    copy_tree(ROOT / "frontend" / "dist", target / "frontend_dist")
    shutil.copytree(
        ROOT / "backend",
        target / "backend",
        ignore=shutil.ignore_patterns(".mypy_cache", ".pytest_cache", "__pycache__"),
    )
    shutil.copytree(ROOT / "scripts" / "package" / "assets", target / "assets")
    shutil.copy(ROOT / ".env.example", target / ".env.example")
    shutil.copy(ROOT / "README.md", target / "README.md")
    if platform == "windows":
        (target / "start-longview.bat").write_text(
            '@echo off\r\ncd /d "%~dp0backend"\r\npython -m app.launcher\r\n',
            encoding="utf-8",
        )
    else:
        script = target / "start-longview.sh"
        script.write_text(
            '#!/usr/bin/env bash\nset -euo pipefail\ncd "$(dirname "$0")/backend"\npython3 -m app.launcher\n',
            encoding="utf-8",
        )
        script.chmod(0o755)
    (target / "PACKAGE-NOTES.md").write_text(
        f"# LongView Markets {VERSION}\n\nThis package includes the branded icon assets and a WebView app-frame launcher. Native PyInstaller executables are prepared by the release workflow when supported by the runner.\n",
        encoding="utf-8",
    )
    return target


def archive(path: Path, platform: str) -> Path:
    if platform == "windows":
        output = DIST / "LongView-Markets-windows.zip"
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as bundle:
            for file in path.rglob("*"):
                bundle.write(file, file.relative_to(path.parent))
        return output
    output = DIST / f"LongView-Markets-{platform}.tar.gz"
    with tarfile.open(output, "w:gz") as bundle:
        bundle.add(path, arcname=path.name)
    return output


def main() -> int:
    DIST.mkdir(exist_ok=True)
    for required in ["longview-icon.ico", "longview-icon.icns", "longview-icon.png"]:
        if not (ROOT / "scripts" / "package" / "assets" / required).exists():
            raise SystemExit(f"Missing branded icon asset: {required}")
    outputs = [
        archive(stage_platform(platform), platform)
        for platform in ["windows", "linux", "macos"]
    ]
    checksums = []
    for output in outputs:
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        checksums.append(f"{digest}  {output.name}")
    (DIST / "checksums.txt").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    print("Release artifacts ready:")
    for output in outputs:
        print(f"- {output}")
    print(f"- {DIST / 'checksums.txt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
