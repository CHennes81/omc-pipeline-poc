"""Configuration management for the API."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql://localhost/omc_pipeline_poc"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    app_env: str = "local"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

