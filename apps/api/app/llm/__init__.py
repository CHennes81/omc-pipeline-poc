"""Provider-neutral LLM layer. Import from here, never from a vendor SDK.

    from app.llm import LLMRequest, LLMMessage, create_provider
"""
from app.llm.base import LLMMessage, LLMProvider, LLMRequest, LLMResponse
from app.llm.errors import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMConnectionError,
    LLMError,
    LLMQuotaError,
    LLMRateLimitError,
    LLMRequestError,
    LLMResponseError,
    LLMServiceError,
    LLMTimeoutError,
)
from app.llm.factory import create_provider, is_provider_configured, known_provider_names

__all__ = [
    "LLMMessage",
    "LLMProvider",
    "LLMRequest",
    "LLMResponse",
    "LLMError",
    "LLMAuthenticationError",
    "LLMConfigurationError",
    "LLMConnectionError",
    "LLMQuotaError",
    "LLMRateLimitError",
    "LLMRequestError",
    "LLMResponseError",
    "LLMServiceError",
    "LLMTimeoutError",
    "create_provider",
    "is_provider_configured",
    "known_provider_names",
]
