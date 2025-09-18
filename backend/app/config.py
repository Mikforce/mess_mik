from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env", "../../.env"), env_file_encoding="utf-8", env_prefix="")

    # App
    APP_NAME: str = "Messenger Backend"
    ENV: str = "dev"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "change-me-in-.env"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/postgres"

    # Encryption
    MEDIA_ENC_KEY: str = ""  # base64 urlsafe 32 bytes for Fernet; if empty, media will be stored plaintext


class RuntimeConfig(BaseModel):
    settings: Settings


@lru_cache()
def get_settings() -> Settings:
    return Settings()


