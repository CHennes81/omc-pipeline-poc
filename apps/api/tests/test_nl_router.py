"""NLRouter driven through the provider-neutral interface with a fake provider.

Verifies the Appendix G behavior that must survive the provider swap: pick one intent from
the enumerated registry, gate on confidence, allow exactly one clarification round.
"""
import json

import pytest

from app.llm import (
    LLMAuthenticationError,
    LLMConnectionError,
    LLMProvider,
    LLMQuotaError,
    LLMResponse,
    LLMResponseError,
    LLMTimeoutError,
)
from app.nl_router import ROUTER_SYSTEM_PROMPT, IntentRegistry, NLRouter, RoutingStatus

PRODUCTION = {"production_code": "EXFTR"}


class FakeProvider(LLMProvider):
    name = "fake"

    def __init__(self, reply=None, raises=None):
        super().__init__(model="fake-model")
        self.reply = reply
        self.raises = raises
        self.requests = []

    def generate(self, request):
        self.requests.append(request)
        if self.raises:
            raise self.raises
        text = self.reply if isinstance(self.reply, str) else json.dumps(self.reply)
        return LLMResponse(text=text, provider=self.name, model=self.model)


def _reply(intent_id="latest_camera_original", confidence=0.95, params=None, missing=None,
           ambiguity=None, user_message=None):
    return {
        "intent_id": intent_id,
        "confidence": confidence,
        "params": {"shot_code": "011_001"} if params is None else params,
        "missing_params": missing or [],
        "ambiguity": ambiguity,
        "user_message": user_message,
    }


def _route(provider, question="latest camera original for shot 011_001", **kwargs):
    router = NLRouter(IntentRegistry(), provider)
    return router.route(question, session_context=dict(PRODUCTION), **kwargs)


def test_confident_match_is_ok():
    result = _route(FakeProvider(_reply()))
    assert result.status == RoutingStatus.OK
    assert result.intent_id == "latest_camera_original"
    assert result.params == {"shot_code": "011_001"}


def test_prompt_sends_the_enumerated_intents_and_requests_json():
    provider = FakeProvider(_reply())
    _route(provider)
    request = provider.requests[0]
    assert request.json_output is True
    assert request.system == ROUTER_SYSTEM_PROMPT
    user_text = request.messages[0].content
    registry = IntentRegistry()
    for intent in registry.get_all_intents():
        assert intent["intent_id"] in user_text  # the model only chooses from this list


def test_missing_param_asks_one_clarifying_question():
    reply = _reply(params={}, missing=["shot_code"], confidence=0.7)
    result = _route(FakeProvider(reply), question="latest camera original")
    assert result.status == RoutingStatus.NEEDS_CLARIFICATION
    assert result.intent_id == "latest_camera_original"
    # Regression: the descriptions are gerunds, so this once read "To checking ...".
    assert result.user_message == (
        "To start checking the latest camera original, I need a shot code. "
        "Can you provide it?"
    )


def test_second_pass_still_unresolved_is_unanswerable():
    """Appendix G: at most ONE follow-up; the second attempt must not ask again."""
    reply = _reply(params={}, missing=["shot_code"], confidence=0.7)
    result = _route(FakeProvider(reply), question="the first one",
                    is_clarification=True)
    assert result.status == RoutingStatus.UNANSWERABLE


def test_low_confidence_is_unanswerable():
    reply = _reply(intent_id=None, confidence=0.2, params={}, user_message="Not supported")
    assert _route(FakeProvider(reply), question="what's the weather").status == RoutingStatus.UNANSWERABLE


def test_unregistered_intent_is_rejected():
    result = _route(FakeProvider(_reply(intent_id="drop_all_tables")))
    assert result.status == RoutingStatus.UNANSWERABLE
    assert result.error_code == "invalid_intent_id"


def test_non_json_reply_is_unanswerable():
    result = _route(FakeProvider("I think you want the camera original."))
    assert result.status == RoutingStatus.UNANSWERABLE
    assert result.error_code == "llm_invalid_json"


@pytest.mark.parametrize(
    "error, code",
    [
        (LLMTimeoutError("slow"), "llm_timeout"),
        (LLMConnectionError("down"), "llm_timeout"),
        (LLMAuthenticationError("bad key"), "llm_unavailable"),
        (LLMQuotaError("no credits"), "llm_unavailable"),
        (LLMResponseError("refused"), "llm_bad_response"),
    ],
)
def test_llm_failures_map_to_router_errors(error, code):
    result = _route(FakeProvider(raises=error))
    assert result.status == RoutingStatus.ERROR
    assert result.error_code == code
