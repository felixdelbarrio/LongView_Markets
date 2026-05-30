from __future__ import annotations

from pathlib import Path

import typer

from app.db.database import ensure_database
from app.repositories.demo_repository import ensure_demo_files

app = typer.Typer(help="LongView Markets internal CLI")


@app.command()
def seed(project_root: Path = typer.Option(Path(".."), help="Repository root")) -> None:
    root = project_root.resolve()
    status = ensure_demo_files(root)
    ensure_database(root / "data" / "longview.sqlite")
    typer.echo(f"Seed data ready: {status}")


if __name__ == "__main__":
    app()
