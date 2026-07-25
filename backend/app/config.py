from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "SitePulse"
    app_version: str = "1.0.0"
    app_env: Literal["development", "test", "production"] = "development"
    api_prefix: str = "/api/v1"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 480

    database_url: str = "sqlite:///./sitepulse.db"
    redis_url: str = "redis://localhost:6379/0"
    celery_always_eager: bool = False

    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["http://localhost:3000"])
    allow_private_networks: bool = False
    allowed_private_hosts: Annotated[list[str], NoDecode] = Field(default_factory=lambda: ["demo-target", "localhost"])
    request_timeout_seconds: float = 15.0
    max_response_bytes: int = 2_000_000
    max_redirects: int = 5
    max_scrape_attempts: int = 3
    retry_backoff_seconds: float = 0.5
    user_agent: str = "SitePulse/1.0 (+https://github.com/)"

    seed_demo_data: bool = True
    demo_target_base_url: str = "http://localhost:8080"

    smtp_enabled: bool = False
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = False
    default_notification_email: str = "demo@sitepulse.local"

    log_level: str = "INFO"

    @field_validator("cors_origins", "allowed_private_hosts", mode="before")
    @classmethod
    def split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache

def get_settings() -> Settings:
    return Settings()
