from pathlib import Path
from functools import lru_cache
from typing import Annotated
from enum import StrEnum

from fastapi import Depends
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnv(StrEnum):
    DEVELOP = "develop"
    PROD = "prod"
    LOCAL = "local"


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Forum API"
    DEBUG: bool = True

    APP_ENV: AppEnv = AppEnv.DEVELOP

    SQLITE_DATABASE_URL: str = "sqlite:///./forum.db"

    POSTGRES_URL: str | None = None

    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str
    JWT_ALGORITHM: str = "RS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.APP_ENV == AppEnv.PROD:
            url = self.POSTGRES_URL or ""
            if url.startswith("postgresql://"):
                return url.replace(
                    "postgresql://",
                    "postgresql+asyncpg://",
                )
            return url

        url = self.SQLITE_DATABASE_URL
        if url.startswith("sqlite://"):
            return url.replace(
                "sqlite://",
                "sqlite+aiosqlite://",
            )
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
settings = get_settings()
