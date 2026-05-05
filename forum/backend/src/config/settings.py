from pathlib import Path
from functools import lru_cache
from typing import Annotated, Literal

from fastapi import Depends
from pydantic import (
    AliasChoices,
    Field,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
AppEnv = Literal["develop", "prod"]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Forum API"
    DEBUG: bool = True
    APP_ENV: AppEnv = "develop"
    SQLITE_DATABASE_URL: str = "sqlite:///./forum.db"
    POSTGRES_URL: str | None = Field(
        default=None,
        validation_alias=AliasChoices("POSTGRES_URL", "POSTGRESS_URL", "POTGRESS_URL"),
    )
    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("JWT_PRIVATE_KEY", "JWT_PUBLIC_KEY", mode="before")
    @classmethod
    def normalize_pem_key(cls, value: str) -> str:
        return value.replace("\\n", "\n") if isinstance(value, str) else value

    @field_validator("APP_ENV", mode="before")
    @classmethod
    def normalize_app_env(cls, value: str) -> str:
        aliases = {
            "dev": "develop",
            "devlop": "develop",
            "developement": "develop",
            "development": "develop",
            "develop": "develop",
            "local": "develop",
            "pod": "prod",
            "prod": "prod",
            "production": "prod",
        }
        normalized = str(value).strip().lower()
        return aliases.get(normalized, normalized)

    @model_validator(mode="after")
    def validate_database_selection(self) -> "Settings":
        if self.APP_ENV == "prod" and not self.POSTGRES_URL:
            raise ValueError("POSTGRES_URL is required when APP_ENV=prod")
        return self

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        if self.APP_ENV == "prod":
            url = self.POSTGRES_URL or ""
            return url.replace("postgresql://", "postgresql+asyncpg://") if url.startswith("postgresql://") else url

        url = self.SQLITE_DATABASE_URL
        return url.replace("sqlite://", "sqlite+aiosqlite://") if url.startswith("sqlite://") else url

@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
settings = get_settings()
