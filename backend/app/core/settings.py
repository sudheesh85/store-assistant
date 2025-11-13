from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # API metadata
    API_TITLE: str = Field(default="Store Assistant API")
    API_VERSION: str = Field(default="0.1.0")
    API_PREFIX: str = Field(default="/api/v1")

    # CORS
    ALLOWED_ORIGINS: List[str] | str = Field(default_factory=lambda: [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ])

    # OpenAI / LLM settings
    OPENAI_API_KEY: str | None = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")
    OPENAI_TEMPERATURE: float = Field(default=0.0)

    # Data storage
    DATA_STORAGE_PATH: Path = Field(default=Path("./storage"))
    MAX_UPLOAD_MB: int = Field(default=25, ge=1, le=150)
    DEFAULT_STORE_ID: str = Field(default="demo-store")

    # Query limits
    MAX_ROWS: int = Field(default=1000, ge=1)
    PREVIEW_ROWS: int = Field(default=5, ge=1, le=100)  # Rows to show in UI
    QUERY_TIMEOUT: int = Field(default=30, ge=1)

    # Feature toggles
    ENABLE_VISUALIZATION_SUGGESTIONS: bool = Field(default=True)
    ENABLE_RESULT_EXPLANATION: bool = Field(default=True)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, value: List[str] | str) -> List[str]:
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @field_validator("DATA_STORAGE_PATH", mode="after")
    @classmethod
    def _ensure_storage_path(cls, value: Path) -> Path:
        value.mkdir(parents=True, exist_ok=True)
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
