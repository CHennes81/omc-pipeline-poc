"""Provider-neutral LLM interface.

The application talks to a language model only through ``LLMProvider.generate``. Nothing
outside ``app/llm/providers/`` may import a vendor SDK.

Design notes
------------
* The request carries only what *any* chat-style model needs: an optional system prompt, a
  list of role/content messages, an output budget, and a "reply with JSON" flag.
* Vendor tuning knobs (sampling temperature, reasoning effort, model name, ...) are NOT part
  of the request. They belong to the provider's own configuration, because they differ by
  vendor and even by model generation (some models reject ``temperature`` outright).
* ``json_output=True`` is a *request*, not a guarantee of schema. Providers do their best
  (native JSON mode where one exists, otherwise instructions plus tolerant extraction), and
  the caller still parses and validates the result.
* Calls are synchronous; callers that need async run them in a worker thread.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Literal, Optional, Sequence

Role = Literal["user", "assistant"]


@dataclass(frozen=True)
class LLMMessage:
    role: Role
    content: str


@dataclass(frozen=True)
class LLMRequest:
    messages: Sequence[LLMMessage]
    system: Optional[str] = None
    max_tokens: int = 1024
    json_output: bool = False
    timeout_seconds: Optional[float] = None


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    stop_reason: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None


class LLMProvider(ABC):
    """A configured connection to one model on one vendor's API."""

    #: Registry name, e.g. "anthropic". Also reported in logs and traces.
    name: ClassVar[str]

    def __init__(self, model: str) -> None:
        self.model = model

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Run one completion.

        Raises:
            LLMError (or a subclass): for every failure. Vendor exceptions never escape.
        """
