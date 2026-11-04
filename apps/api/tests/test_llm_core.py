"""Provider-neutral pieces: JSON extraction, factory selection, settings validation."""
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.config import Settings
from app.llm import (
    LLMConfigurationError,
    LLMConnectionError,
    LLMTimeoutError,
    create_provider,
    is_provider_configured,
    known_provider_names,
)
from app.llm.json_utils import extract_json_text


# ---- json_utils -------------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw, expected",
    [
        ('{"a": 1}', '{"a": 1}'),
        ('  {"a": 1}\n', '{"a": 1}'),
        ('```json\n{"a": 1}\n```', '{"a": 1}'),
        ('```\n{"a": 1}\n```', '{"a": 1}'),
        ('Sure! Here you go: {"a": {"b": 2}} Hope that helps.', '{"a": {"b": 2}}'),
        ("no json here", "no json here"),
        ("", ""),
    ],
)
def test_extract_json_text(raw, expected):
    assert extract_json_text(raw) == expected


# ---- error types keep working with the existing builtin-based handlers ---------------------

def test_timeout_and_connection_errors_are_builtin_subclasses():
    assert issubclass(LLMTimeoutError, TimeoutError)
    assert issubclass(LLMConnectionError, ConnectionError)


# ---- factory ----------------------------------------------------------------------------

def _settings(**overrides):
    base = dict(
        llm_provider="anthropic",
        llm_model=None,
        anthropic_api_key="sk-ant-test",
        anthropic_effort="low",
        openai_api_key=None,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_known_providers():
    assert known_provider_names() == ("anthropic", "openai")


def test_default_provider_is_anthropic_haiku():
    provider = create_provider(_settings())
    assert provider.name == "anthropic"
    assert provider.model == "claude-haiku-5-5"


def test_model_override_for_sonnet_demo():
    provider = create_provider(_settings(llm_model="claude-sonnet-5-5"))
    assert provider.model == "claude-sonnet-5-5"


def test_openai_provider_is_selectable_but_inactive_by_default():
    provider = create_provider(_settings(llm_provider="openai", openai_api_key="sk-test"))
    assert provider.name == "openai"
    assert provider.model == "gpt-4o-mini"


def test_missing_key_is_a_configuration_error():
    with pytest.raises(LLMConfigurationError, match="ANTHROPIC_API_KEY"):
        create_provider(_settings(anthropic_api_key=None))


def test_unknown_provider_is_a_configuration_error():
    with pytest.raises(LLMConfigurationError, match="Unknown LLM_PROVIDER"):
        create_provider(_settings(llm_provider="nope"))


def test_is_provider_configured():
    assert is_provider_configured(_settings())
    assert not is_provider_configured(_settings(anthropic_api_key=None))
    assert not is_provider_configured(_settings(anthropic_api_key=""))
    assert not is_provider_configured(_settings(llm_provider="nope"))
    # only the SELECTED provider's key counts
    assert not is_provider_configured(_settings(anthropic_api_key=None, openai_api_key="sk-x"))


# ---- Settings ---------------------------------------------------------------------------

def test_settings_rejects_unknown_provider():
    with pytest.raises(ValidationError):
        Settings(llm_provider="gemini", _env_file=None)


def test_settings_normalizes_provider_name():
    assert Settings(llm_provider=" Anthropic ", _env_file=None).llm_provider == "anthropic"


def test_nl_enabled_requires_flag_and_selected_providers_key():
    assert not Settings(_env_file=None, ask_nl_enabled=True).is_nl_enabled()  # no key
    assert not Settings(_env_file=None, anthropic_api_key="k").is_nl_enabled()  # flag off
    assert Settings(_env_file=None, ask_nl_enabled=True, anthropic_api_key="k").is_nl_enabled()
    # an OpenAI key alone does not enable NL while anthropic is the selected provider
    assert not Settings(_env_file=None, ask_nl_enabled=True, openai_api_key="k").is_nl_enabled()
