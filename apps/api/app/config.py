"""Configuration management for the API."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = "postgresql://localhost/omc_pipeline_poc"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    app_env: str = "local"

    # Natural Language Ask Configuration (Appendix G)
    openai_api_key: Optional[str] = None
    ask_nl_enabled: bool = False
    ask_dual_mode_ui: bool = False
    ask_default_mode: str = "deterministic"  # "deterministic" or "nl"
    ask_nl_confidence_min: float = 0.80
    ask_nl_confidence_clarify_min: float = 0.60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def is_nl_enabled(self) -> bool:
        """Check if NL Ask is properly configured and enabled."""
        return self.ask_nl_enabled and self.openai_api_key is not None


settings = Settings()
