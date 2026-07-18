from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TaleDrop-Novellaire"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/taledrop_novellaire"
    )

    JWT_SECRET_KEY: str = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    MAIL_USERNAME: str = "example@example.com"
    MAIL_PASSWORD: str = "changeme"
    MAIL_FROM: str = "example@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "TaleDrop-Novellaire"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    FRONTEND_URL: str = "http://localhost:3000"
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Razorpay ---
    RAZORPAY_KEY_ID: str = "rzp_test_changeme"
    RAZORPAY_KEY_SECRET: str = "changeme"

    # --- CORS ---
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    UPLOAD_DIR: str = "uploads"
    STATIC_URL_PREFIX: str = "/static"
    AVATAR_MAX_SIZE_MB: int = 5
    ALLOWED_IMAGE_CONTENT_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    ]

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance so the .env file is parsed once."""
    return Settings()


settings = get_settings()
