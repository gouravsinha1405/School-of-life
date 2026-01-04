from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://lebensschule:lebensschule@localhost:5432/lebensschule"

    @property
    def sqlalchemy_database_url(self) -> str:
        """Convert Render's postgres:// URL to postgresql+psycopg://"""
        url = self.database_url
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg://", 1)
        return url

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60 * 24 * 7

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    groq_api_key: str | None = None
    groq_model_name: str = "gpt-oss-120b"


settings = Settings()  # singleton
