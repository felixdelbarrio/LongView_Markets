from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.router import router
from app.core.config import get_settings
from app.core.constants import APP_NAME
from app.core.logging import configure_logging
from app.core.security import SecurityHeadersMiddleware, SimpleRateLimitMiddleware
from app.repositories import demo_repository

configure_logging()
settings = get_settings()
demo_repository.ensure_demo_files(settings.project_root)

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

frontend_dist = Path(__file__).resolve().parents[2] / "frontend_dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
