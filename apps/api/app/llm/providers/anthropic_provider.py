"""Anthropic (Claude) implementation of ``LLMProvider``. ACTIVE provider.

Notes on current Claude models (verified against the Anthropic SDK docs, 2026-11):
* Sampling parameters (``temperature``, ``top_p``, ``top_k``) are rejected, so none are sent.
  Determinism for intent routing comes from the prompt plus schema validation in the caller.
* There is no native JSON mode without a strict schema, and routing ``params`` are free-form,
  so for ``json_output`` we add an instruction and extract the JSON object from the reply.
* Reasoning depth is controlled with ``output_config.effort``; "low" keeps routing fast.
* Replies can contain non-text blocks (e.g. ``thinking``); only ``text`` blocks are read.
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
from app.llm.json_utils import extract_json_text

DEFAULT_MODEL = "claude-haiku-5-5"

_JSON_INSTRUCTION = (
    "Respond with a single JSON object and nothing else: no markdown fences, no prose."
)


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(
        self,
        api_key: Optional[str],
        model: Optional[str] = None,
        *,
        effort: Optional[str] = "low",
        timeout_seconds: Optional[float] = None,
        client: Any = None,
    ) -> None:
        """
        Args:
            api_key: Anthropic API key (ignored when ``client`` is injected).
            model: Claude model id. Defaults to ``claude-haiku-5-5``.
            effort: ``output_config.effort`` (low|medium|high|xhigh|max), or None for the
                model default.
            timeout_seconds: default per-request timeout.
            client: pre-built ``anthropic.Anthropic`` (used by tests).
        """
        super().__init__(model or DEFAULT_MODEL)
        import anthropic  # imported lazily so other providers don't need this package

        self._sdk = anthropic
        self._effort = effort or None
        if client is not None:
            self._client = client
        else:
            kwargs: dict = {"api_key": api_key}
            if timeout_seconds is not None:
                kwargs["timeout"] = timeout_seconds
            self._client = anthropic.Anthropic(**kwargs)

    def generate(self, request: LLMRequest) -> LLMResponse:
        system = request.system
        if request.json_output:
            system = f"{system}\n\n{_JSON_INSTRUCTION}" if system else _JSON_INSTRUCTION

        params: dict = {
            "model": self.model,
            "max_tokens": request.max_tokens,
            "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        }
        if system:
            params["system"] = system
        if self._effort:
            params["output_config"] = {"effort": self._effort}

        client = self._client
        if request.timeout_seconds is not None:
            client = client.with_options(timeout=request.timeout_seconds)

        try:
            message = client.messages.create(**params)
        except Exception as exc:  # translated below; vendor errors never escape
            raise self._translate(exc) from exc

        if message.stop_reason == "refusal":
            raise LLMResponseError("The model declined to answer (stop_reason=refusal).")
        if message.stop_reason == "max_tokens":
            raise LLMResponseError(
                f"The model's reply was cut off at max_tokens={request.max_tokens}."
            )

        text = "".join(b.text for b in message.content if getattr(b, "type", None) == "text")
        if request.json_output:
            text = extract_json_text(text)

        usage = getattr(message, "usage", None)
        return LLMResponse(
            text=text,
            provider=self.name,
            model=getattr(message, "model", None) or self.model,
            stop_reason=message.stop_reason,
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
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
            return LLMRateLimitError(str(exc))
        if isinstance(exc, sdk.APIStatusError):
            status = exc.status_code
            if status == 402:
                return LLMQuotaError(str(exc))
            if status >= 500:  # includes 529 "overloaded"
                return LLMServiceError(str(exc))
            return LLMRequestError(str(exc))
        return exc  # not an SDK error: let it propagate unchanged
