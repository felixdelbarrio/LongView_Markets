from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    api_host: str = Field(default="127.0.0.1", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    frontend_url: str = Field(default="http://localhost:5173", alias="FRONTEND_URL")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", alias="CORS_ORIGINS")
    base_currency: str = Field(default="EUR", alias="BASE_CURRENCY")
    data_provider: str = Field(default="mock", alias="DATA_PROVIDER")
    external_gpt_url: str = Field(
        default="https://chatgpt.com/g/g-longview-markets", alias="EXTERNAL_GPT_URL"
    )
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3])

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"


@lru_cache
def get_settings() -> Settings:
    return Settings()
