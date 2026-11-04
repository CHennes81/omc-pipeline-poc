"""Provider-neutral LLM errors.

Every provider module translates its vendor SDK's exceptions into these types, so the
rest of the application never imports (or catches) a vendor exception class.

Timeout and connection errors also inherit from the matching builtin (``TimeoutError`` /
``ConnectionError``). Existing handlers in ``nl_router`` and ``routes`` already catch those
builtins to report "remote services unavailable", and keep working unchanged.
"""


class LLMError(Exception):
    """Base class for all LLM-layer failures."""


class LLMConfigurationError(LLMError):
    """The provider is unknown or not configured (e.g. missing API key)."""


class LLMTimeoutError(LLMError, TimeoutError):
    """The request timed out."""


class LLMConnectionError(LLMError, ConnectionError):
    """The provider could not be reached (network failure before a response)."""


class LLMAuthenticationError(LLMError):
    """The provider rejected our credentials or permissions."""


class LLMQuotaError(LLMError):
    """The account is out of credits / over its spending quota."""


class LLMRateLimitError(LLMError):
    """The provider is rate limiting us. Retrying later may succeed."""


class LLMServiceError(LLMError):
    """The provider failed or is overloaded (5xx). Retrying later may succeed."""


class LLMRequestError(LLMError):
    """The provider rejected the request itself (4xx). Retrying will not help."""


class LLMResponseError(LLMError):
    """The provider answered, but not usably (refusal, truncated output, ...)."""
