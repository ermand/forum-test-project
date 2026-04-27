from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str = "Forum API"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./forum.db"
    SECRET_KEY : str = "fefefed0bce0950b0df9628fd4fd385da311584aa33d7578599c4dc342f5405a"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()