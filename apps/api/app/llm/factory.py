"""Select and build the configured ``LLMProvider``.

To add a provider: write a module in ``app/llm/providers/`` implementing ``LLMProvider``,
add one entry to ``_PROVIDERS`` below, and add its API key (and any tuning options) to
``app.config.Settings``. Nothing else in the application changes.

Provider modules are imported lazily, so an inactive provider's SDK need not be installed.
This module deliberately does not import ``app.config`` (the settings object is passed in),
because ``app.config`` imports this module to validate ``LLM_PROVIDER``.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from app.llm.base import LLMProvider
from app.llm.errors import LLMConfigurationError


@dataclass(frozen=True)
class _ProviderSpec:
    module: str
    class_name: str
    api_key_setting: str  # attribute on Settings holding this vendor's API key
    options: Dict[str, str]  # provider __init__ kwarg -> Settings attribute


_PROVIDERS: Dict[str, _ProviderSpec] = {
    "anthropic": _ProviderSpec(
        module="app.llm.providers.anthropic_provider",
        class_name="AnthropicProvider",
        api_key_setting="anthropic_api_key",
        options={"effort": "anthropic_effort"},
    ),
    "openai": _ProviderSpec(
        module="app.llm.providers.openai_provider",
        class_name="OpenAIProvider",
        api_key_setting="openai_api_key",
        options={},
    ),
}


def known_provider_names() -> Tuple[str, ...]:
    return tuple(sorted(_PROVIDERS))


def _spec_for(name: str) -> _ProviderSpec:
    try:
        return _PROVIDERS[name]
    except KeyError:
        raise LLMConfigurationError(
            f"Unknown LLM_PROVIDER {name!r}. Known providers: {', '.join(known_provider_names())}."
        ) from None


def is_provider_configured(settings: Any) -> bool:
    """True when the selected provider exists and has an API key. Never raises."""
    spec = _PROVIDERS.get(settings.llm_provider)
    return bool(spec and getattr(settings, spec.api_key_setting, None))


def create_provider(settings: Any, *, timeout_seconds: Optional[float] = None) -> LLMProvider:
    """Build the provider named by ``settings.llm_provider``."""
    spec = _spec_for(settings.llm_provider)
    api_key = getattr(settings, spec.api_key_setting, None)
    if not api_key:
        raise LLMConfigurationError(
            f"LLM_PROVIDER={settings.llm_provider} but {spec.api_key_setting.upper()} is not set."
        )

    cls = getattr(importlib.import_module(spec.module), spec.class_name)
    kwargs = {opt: getattr(settings, attr) for opt, attr in spec.options.items()}
    return cls(
        api_key=api_key,
        model=settings.llm_model or None,
        timeout_seconds=timeout_seconds,
        **kwargs,
    )
