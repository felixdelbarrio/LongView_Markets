from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.router import router
from app.core.config import get_settings
from app.core.constants import APP_NAME
from app.core.logging import configure_logging
from app.core.security import SecurityHeadersMiddleware, SimpleRateLimitMiddleware
from app.db.database import ensure_database
from app.repositories import demo_repository

configure_logging()
settings = get_settings()
demo_repository.ensure_demo_files(settings.project_root)
ensure_database(settings.database_path)

app = FastAPI(
    title=APP_NAME,
    version="0.1.0",
    description="Informational and educational long-term investing decision support platform.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SimpleRateLimitMiddleware)
app.include_router(router)


def resolve_frontend_dist() -> Path | None:
    candidates: list[Path] = []
    env_path = os.environ.get("LONGVIEW_FRONTEND_DIST")
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(
        [
            Path(getattr(sys, "_MEIPASS", settings.project_root)) / "frontend_dist",
            settings.project_root / "frontend_dist",
            Path(__file__).resolve().parents[2] / "frontend_dist",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


frontend_dist = resolve_frontend_dist()
if frontend_dist is not None:
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
