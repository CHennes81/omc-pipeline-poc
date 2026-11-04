"""Configuration management for the API."""
import os
from pydantic import field_validator
from pydantic_settings import BaseSettings
from typing import Optional

from app.llm.factory import is_provider_configured, known_provider_names


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost/omc_pipeline_poc")
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    app_env: str = os.getenv("APP_ENV", "local")

    # LLM provider selection (see app/llm). Exactly one provider is active at a time.
    llm_provider: str = "anthropic"  # one of app.llm.factory.known_provider_names()
    llm_model: Optional[str] = None  # None = the provider's default (anthropic: claude-haiku-5-5)
    anthropic_api_key: Optional[str] = None
    anthropic_effort: Optional[str] = "low"  # low|medium|high|xhigh|max; Anthropic only
    openai_api_key: Optional[str] = None  # used only when LLM_PROVIDER=openai (inactive provider)

    # Natural Language Ask Configuration (Appendix G)
    ask_nl_enabled: bool = False
    ask_dual_mode_ui: bool = False
    ask_default_mode: str = "nl"  # "deterministic" or "nl"; NL is only used when ask_nl_enabled and a provider key is configured
    ask_nl_confidence_min: float = 0.80
    ask_nl_confidence_execute_weak_min: float = 0.75
    ask_nl_confidence_clarify_min: float = 0.60
    ask_nl_trace: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @field_validator("llm_provider")
    @classmethod
    def _validate_llm_provider(cls, value: str) -> str:
        name = value.strip().lower()
        if name not in known_provider_names():
            raise ValueError(
                f"LLM_PROVIDER must be one of {', '.join(known_provider_names())} (got {value!r})"
            )
        return name

    def is_nl_enabled(self) -> bool:
        """NL Ask is on AND the selected LLM provider has an API key."""
        return self.ask_nl_enabled and is_provider_configured(self)


settings = Settings()
