from __future__ import annotations

from pathlib import Path

import typer

from app.db.database import ensure_database

app = typer.Typer(help="LongView Markets internal CLI")


@app.command()
def seed(project_root: Path = typer.Option(Path(".."), help="Repository root")) -> None:
    root = project_root.resolve()
    database = ensure_database(root / "data" / "longview.sqlite")
    (root / "data" / "parquet").mkdir(parents=True, exist_ok=True)
    typer.echo(
        {
            "sqlite": str(database),
            "parquet": "ready",
            "demo_mode": "disabled",
        }
    )


if __name__ == "__main__":
    app()
