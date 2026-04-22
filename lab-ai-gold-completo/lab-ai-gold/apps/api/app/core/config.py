"""
Configuração central da aplicação via pydantic-settings.
Lê variáveis do ambiente / .env automaticamente.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "LAB AI GOLD"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ─── Banco de Dados ───────────────────────────────────────────────────────
    DATABASE_URL: str
    DATABASE_SYNC_URL: str = ""

    @field_validator("DATABASE_SYNC_URL", mode="before")
    @classmethod
    def build_sync_url(cls, v: str, info) -> str:
        if v:
            return v
        # Deriva URL síncrona da async automaticamente
        async_url = info.data.get("DATABASE_URL", "")
        return async_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

    # ─── Segurança ────────────────────────────────────────────────────────────
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v) -> List[str]:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # ─── Storage ──────────────────────────────────────────────────────────────
    STORAGE_BACKEND: str = "local"       # "local" | "s3"
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # ─── AWS / R2 (produção) ──────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""

    # ─── Redis (Sprint 5+) ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"

    # ─── Helpers ──────────────────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
