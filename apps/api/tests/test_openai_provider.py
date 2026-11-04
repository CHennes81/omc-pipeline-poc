"""The inactive OpenAIProvider must keep working: it is the pre-refactor behavior, preserved.

Skipped automatically when the optional ``openai`` package is not installed.
"""
import json

import httpx
import pytest

openai = pytest.importorskip("openai")

from app.llm import (  # noqa: E402
    LLMAuthenticationError,
    LLMMessage,
    LLMQuotaError,
    LLMRateLimitError,
    LLMRequest,
    LLMResponseError,
)
from app.llm.providers.openai_provider import OpenAIProvider  # noqa: E402


def _provider(handler):
    client = openai.OpenAI(
        api_key="sk-test",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    return OpenAIProvider(api_key=None, client=client)


def _completion(content="{}", finish_reason="stop"):
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 0,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": finish_reason,
            }
        ],
        "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
    }


def _request(**kwargs):
    base = dict(system="SYS", messages=[LLMMessage("user", "hi")], max_tokens=256)
    base.update(kwargs)
    return LLMRequest(**base)


def test_request_shape_matches_pre_refactor_behavior():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=_completion('{"ok": true}'))

    response = _provider(handler).generate(_request(json_output=True, timeout_seconds=4.0))
    body = seen["body"]
    assert body["model"] == "gpt-4o-mini"
    assert body["temperature"] == 0.0
    assert body["response_format"] == {"type": "json_object"}
    assert body["messages"] == [
        {"role": "system", "content": "SYS"},
        {"role": "user", "content": "hi"},
    ]
    assert response.text == '{"ok": true}'
    assert (response.provider, response.input_tokens, response.output_tokens) == ("openai", 5, 3)


def test_no_json_mode_unless_requested():
    seen = {}

    def handler(request):
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=_completion())

    _provider(handler).generate(_request())
    assert "response_format" not in seen["body"]


def _error(status, code=None, type_="invalid_request_error"):
    def handler(request):
        return httpx.Response(
            status, json={"error": {"message": "boom", "type": type_, "code": code}}
        )

    return handler


def test_errors_are_translated():
    with pytest.raises(LLMAuthenticationError):
        _provider(_error(401, "invalid_api_key")).generate(_request())
    with pytest.raises(LLMQuotaError):  # the failure that motivated the provider swap
        _provider(_error(429, "insufficient_quota")).generate(_request())
    with pytest.raises(LLMRateLimitError):
        _provider(_error(429, "rate_limit_exceeded")).generate(_request())


def test_truncated_reply_raises_response_error():
    def handler(request):
        return httpx.Response(200, json=_completion(finish_reason="length"))

    with pytest.raises(LLMResponseError):
        _provider(handler).generate(_request())
