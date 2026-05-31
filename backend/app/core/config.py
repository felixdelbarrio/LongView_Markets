from __future__ import annotations

import os
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
    default_language: str = Field(default="es", alias="DEFAULT_LANGUAGE")
    default_theme: str = Field(default="dark", alias="DEFAULT_THEME")
    base_currency: str = Field(default="EUR", alias="BASE_CURRENCY")
    fiscal_country: str = Field(default="ES", alias="FISCAL_COUNTRY")
    timezone: str = Field(default="Europe/Madrid", alias="TIMEZONE")
    default_market_provider: str = Field(default="yfinance", alias="DEFAULT_MARKET_PROVIDER")
    secondary_market_provider: str = Field(default="stooq", alias="SECONDARY_MARKET_PROVIDER")
    news_provider: str = Field(default="yfinance", alias="NEWS_PROVIDER")
    fx_provider: str = Field(default="yfinance", alias="FX_PROVIDER")
    fallback_provider: str = Field(default="stooq", alias="FALLBACK_PROVIDER")
    mock_fallback_enabled: bool = Field(default=False, alias="MOCK_FALLBACK_ENABLED")
    demo_mode_enabled: bool = Field(default=False, alias="DEMO_MODE_ENABLED")
    auto_sync_on_startup: bool = Field(default=False, alias="AUTO_SYNC_ON_STARTUP")
    scheduled_sync_enabled: bool = Field(default=False, alias="SCHEDULED_SYNC_ENABLED")
    scheduled_sync_time: str = Field(default="22:30", alias="SCHEDULED_SYNC_TIME")
    sync_universes: str = Field(
        default="ibex35,eurostoxx50,stoxx_europe_600_sample,nasdaq100,sp500,dax40,cac40,ftse100,ftse_mib,aex25,smi20,psi20,ucits_etf_sample",
        alias="SYNC_UNIVERSES",
    )
    generative_enabled: bool = Field(default=True, alias="GENERATIVE_ENABLED")
    generative_mode: str = Field(default="manual_url", alias="GENERATIVE_MODE")
    generative_external_gpt_url: str = Field(
        default="https://chatgpt.com/g/g-longview-markets",
        alias="GENERATIVE_EXTERNAL_GPT_URL",
    )
    generative_language: str = Field(default="es", alias="GENERATIVE_LANGUAGE")
    generative_prompt_depth: str = Field(default="standard", alias="GENERATIVE_PROMPT_DEPTH")
    generative_include_portfolio: bool = Field(default=True, alias="GENERATIVE_INCLUDE_PORTFOLIO")
    generative_include_news: bool = Field(default=True, alias="GENERATIVE_INCLUDE_NEWS")
    generative_include_forecasts: bool = Field(default=True, alias="GENERATIVE_INCLUDE_FORECASTS")
    generative_include_tax: bool = Field(default=False, alias="GENERATIVE_INCLUDE_TAX")
    generative_include_data_quality: bool = Field(default=True, alias="GENERATIVE_INCLUDE_DATA_QUALITY")
    generative_auto_prepare_daily_jobs: bool = Field(default=True, alias="GENERATIVE_AUTO_PREPARE_DAILY_JOBS")
    generative_auto_import_allowed: bool = Field(default=False, alias="GENERATIVE_AUTO_IMPORT_ALLOWED")
    generative_json_repair_enabled: bool = Field(default=True, alias="GENERATIVE_JSON_REPAIR_ENABLED")
    generative_store_history: bool = Field(default=True, alias="GENERATIVE_STORE_HISTORY")
    generative_max_context_items: int = Field(default=50, alias="GENERATIVE_MAX_CONTEXT_ITEMS")
    generative_confidence_threshold: float = Field(default=0.60, alias="GENERATIVE_CONFIDENCE_THRESHOLD")
    generative_include_sensitive_portfolio_details: bool = Field(
        default=False, alias="GENERATIVE_INCLUDE_SENSITIVE_PORTFOLIO_DETAILS"
    )
    external_gpt_url: str = Field(
        default="https://chatgpt.com/g/g-longview-markets", alias="EXTERNAL_GPT_URL"
    )
    project_root: Path = Field(
        default_factory=lambda: Path(
            os.environ.get("LONGVIEW_PROJECT_ROOT", Path(__file__).resolve().parents[3])
        ).resolve(),
        alias="LONGVIEW_PROJECT_ROOT",
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def database_path(self) -> Path:
        return self.data_dir / "longview.sqlite"

    @property
    def sync_universe_ids(self) -> list[str]:
        return [item.strip() for item in self.sync_universes.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
