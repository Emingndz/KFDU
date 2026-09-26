from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Uygulama ---
    ENV: str = "dev"
    APP_NAME: str = "KFDU"
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    DATABASE_URL: str = "sqlite:///./kfdu.db"
    CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    FRONTEND_URL: str = "http://localhost:5173"
    CONTACT_EMAIL: str = ""
    MEDIA_DIR: str = "media"

    # --- TMDB (film / dizi) ---
    TMDB_API_KEY: str = ""
    TMDB_LANGUAGE: str = "tr-TR"
    TMDB_REGION: str = "TR"

    # --- Kitaplar ---
    BOOK_PROVIDER: str = "openlibrary"
    GOOGLE_BOOKS_API_KEY: str = ""

    # --- E-posta ---
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM_NAME: str = "KFDU"

    # --- Yapay zekâ (Faz 6) ---
    NVIDIA_API_KEY: str = ""
    LLM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    LLM_MODEL: str = "deepseek-ai/deepseek-v4.1-flash"
    LLM_FALLBACK_MODELS: Annotated[list[str], NoDecode] = []
    LLM_TIMEOUT_SECONDS: int = 20
    ASSISTANT_RATE_LIMIT: str = "20/hour"

    # --- Test ---
    FAKE_PROVIDERS: bool = False

    @field_validator("CORS_ORIGINS", "LLM_FALLBACK_MODELS", mode="before")
    @classmethod
    def _split_csv(cls, v: object) -> object:
        return [s.strip() for s in v.split(",") if s.strip()] if isinstance(v, str) else v


settings = Settings()
