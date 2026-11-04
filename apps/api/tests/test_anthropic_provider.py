"""AnthropicProvider against the REAL Anthropic SDK with a mocked HTTP transport.

No network and no API key: we assert the exact request the SDK would send and how replies
and errors are translated.
"""
import json

import anthropic
import httpx2
import pytest

from app.llm import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMMessage,
    LLMQuotaError,
    LLMRateLimitError,
    LLMRequest,
    LLMRequestError,
    LLMResponseError,
    LLMServiceError,
    LLMTimeoutError,
)
from app.llm.providers.anthropic_provider import AnthropicProvider


def _message_json(text="{}", stop_reason="end_turn", extra_blocks=()):
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "model": "claude-haiku-5-5",
        "content": [*extra_blocks, {"type": "text", "text": text}],
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": {"input_tokens": 11, "output_tokens": 7},
    }


def _provider(handler, **kwargs):
    client = anthropic.Anthropic(
        api_key="sk-ant-test",
        max_retries=0,
        http_client=anthropic.DefaultHttpxClient(transport=httpx2.MockTransport(handler)),
    )
    return AnthropicProvider(api_key=None, client=client, **kwargs)


def _request(**kwargs):
    base = dict(system="SYS", messages=[LLMMessage("user", "hello")], max_tokens=512)
    base.update(kwargs)
    return LLMRequest(**base)


def test_request_shape_and_json_reply_extraction():
    seen = {}

    def handler(request: httpx2.Request):
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content)
        reply = _message_json(
            text='```json\n{"intent_id": "x"}\n```',
            extra_blocks=[{"type": "thinking", "thinking": "", "signature": "sig"}],
        )
        return httpx2.Response(200, json=reply)

    provider = _provider(handler)
    response = provider.generate(_request(json_output=True, timeout_seconds=5.0))

    body = seen["body"]
    assert seen["path"] == "/v1/messages"
    assert body["model"] == "claude-haiku-5-5"
    assert body["max_tokens"] == 512
    assert body["messages"] == [{"role": "user", "content": "hello"}]
    assert body["system"].startswith("SYS") and "single JSON object" in body["system"]
    assert body["output_config"] == {"effort": "low"}
    # current Claude models reject sampling params: none may be sent
    assert not {"temperature", "top_p", "top_k"} & set(body)

    assert response.text == '{"intent_id": "x"}'  # fence stripped, thinking block ignored
    assert (response.provider, response.model, response.stop_reason) == (
        "anthropic",
        "claude-haiku-5-5",
        "end_turn",
    )
    assert (response.input_tokens, response.output_tokens) == (11, 7)


def test_model_and_effort_are_configurable():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return httpx2.Response(200, json=_message_json())

    _provider(handler, model="claude-sonnet-5-5", effort="high").generate(_request())
    assert seen["body"]["model"] == "claude-sonnet-5-5"
    assert seen["body"]["output_config"] == {"effort": "high"}
    assert seen["body"]["system"] == "SYS"  # no JSON instruction unless json_output


def test_effort_none_omits_output_config():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return httpx2.Response(200, json=_message_json())

    _provider(handler, effort=None).generate(_request(system=None))
    assert "output_config" not in seen["body"] and "system" not in seen["body"]


@pytest.mark.parametrize(
    "status, error_type, expected",
    [
        (401, "authentication_error", LLMAuthenticationError),
        (403, "permission_error", LLMAuthenticationError),
        (402, "billing_error", LLMQuotaError),
        (429, "rate_limit_error", LLMRateLimitError),
        (500, "api_error", LLMServiceError),
        (529, "overloaded_error", LLMServiceError),
        (400, "invalid_request_error", LLMRequestError),
    ],
)
def test_http_errors_are_translated(status, error_type, expected):
    def handler(request):
        return httpx2.Response(
            status, json={"type": "error", "error": {"type": error_type, "message": "boom"}}
        )

    with pytest.raises(expected):
        _provider(handler).generate(_request())


def test_timeout_is_translated_and_is_a_builtin_timeout():
    def handler(request):
        raise httpx2.ReadTimeout("slow", request=request)

    with pytest.raises(LLMTimeoutError) as info:
        _provider(handler).generate(_request())
    assert isinstance(info.value, TimeoutError)


def test_connection_failure_is_translated_and_is_a_builtin_connection_error():
    def handler(request):
        raise httpx2.ConnectError("down", request=request)

    with pytest.raises(LLMConnectionError) as info:
        _provider(handler).generate(_request())
    assert isinstance(info.value, ConnectionError)


@pytest.mark.parametrize("stop_reason", ["refusal", "max_tokens"])
def test_unusable_replies_raise_response_error(stop_reason):
    def handler(request):
        return httpx2.Response(200, json=_message_json(stop_reason=stop_reason))

    with pytest.raises(LLMResponseError):
        _provider(handler).generate(_request())
