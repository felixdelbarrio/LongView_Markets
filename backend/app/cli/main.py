from __future__ import annotations

from pathlib import Path

import typer

from app.repositories.demo_repository import ensure_demo_files

app = typer.Typer(help="LongView Markets internal CLI")


@app.command()
def seed(project_root: Path = typer.Option(Path(".."), help="Repository root")) -> None:
    status = ensure_demo_files(project_root.resolve())
    typer.echo(f"Seed data ready: {status}")


if __name__ == "__main__":
    app()
