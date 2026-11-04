"""OpenAI implementation of ``LLMProvider``. INACTIVE (kept for reuse).

This is the logic that used to live directly in ``nl_router.py``, moved behind the neutral
interface. Select it with ``LLM_PROVIDER=openai`` and ``OPENAI_API_KEY``. The ``openai``
package is not in ``requirements.txt``; install it with ``pip install -r requirements-openai.txt``.
"""
from __future__ import annotations

from typing import Any, Optional

from app.llm.base import LLMProvider, LLMRequest, LLMResponse
from app.llm.errors import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMQuotaError,
    LLMRateLimitError,
    LLMRequestError,
    LLMResponseError,
    LLMServiceError,
    LLMTimeoutError,
)

DEFAULT_MODEL = "gpt-4o-mini"


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(
        self,
        api_key: Optional[str],
        model: Optional[str] = None,
        *,
        temperature: float = 0.0,
        timeout_seconds: Optional[float] = None,
        client: Any = None,
    ) -> None:
        super().__init__(model or DEFAULT_MODEL)
        try:
            import openai  # lazy: the package is optional
        except ImportError as exc:
            from app.llm.errors import LLMConfigurationError

            raise LLMConfigurationError(
                "LLM_PROVIDER=openai needs the 'openai' package: "
                "pip install -r requirements-openai.txt"
            ) from exc

        self._sdk = openai
        self._temperature = temperature
        if client is not None:
            self._client = client
        else:
            kwargs: dict = {"api_key": api_key}
            if timeout_seconds is not None:
                kwargs["timeout"] = timeout_seconds
            self._client = openai.OpenAI(**kwargs)

    def generate(self, request: LLMRequest) -> LLMResponse:
        messages: list = []
        if request.system:
            messages.append({"role": "system", "content": request.system})
        messages.extend({"role": m.role, "content": m.content} for m in request.messages)

        params: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": self._temperature,
            "max_tokens": request.max_tokens,
        }
        if request.json_output:
            params["response_format"] = {"type": "json_object"}

        client = self._client
        if request.timeout_seconds is not None:
            client = client.with_options(timeout=request.timeout_seconds)

        try:
            completion = client.chat.completions.create(**params)
        except Exception as exc:
            raise self._translate(exc) from exc

        choice = completion.choices[0]
        if choice.finish_reason == "length":
            raise LLMResponseError(
                f"The model's reply was cut off at max_tokens={request.max_tokens}."
            )
        if choice.finish_reason == "content_filter":
            raise LLMResponseError("The reply was blocked by the provider's content filter.")

        usage = getattr(completion, "usage", None)
        return LLMResponse(
            text=choice.message.content or "",
            provider=self.name,
            model=getattr(completion, "model", None) or self.model,
            stop_reason=choice.finish_reason,
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
        )

    def _translate(self, exc: Exception) -> Exception:
        sdk = self._sdk
        # Order matters: APITimeoutError is a subclass of APIConnectionError.
        if isinstance(exc, sdk.APITimeoutError):
            return LLMTimeoutError(str(exc))
        if isinstance(exc, sdk.APIConnectionError):
            return LLMConnectionError(str(exc))
        if isinstance(exc, (sdk.AuthenticationError, sdk.PermissionDeniedError)):
            return LLMAuthenticationError(str(exc))
        if isinstance(exc, sdk.RateLimitError):
            # OpenAI reports exhausted credits as a 429 with code "insufficient_quota".
            if getattr(exc, "code", None) == "insufficient_quota":
                return LLMQuotaError(str(exc))
            return LLMRateLimitError(str(exc))
        if isinstance(exc, sdk.APIStatusError):
            if exc.status_code >= 500:
                return LLMServiceError(str(exc))
            return LLMRequestError(str(exc))
        return exc
