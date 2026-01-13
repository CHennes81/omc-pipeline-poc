"""Natural Language Ask router with LLM-based intent resolution.

This module implements Appendix G requirements for deterministic NL routing:
- Intent selection from allowlist
- Parameter extraction
- Uncertainty signaling
- Confidence gating
- Clarification loop (max 1 follow-up)
"""
import json
import re
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI
from app.config import settings


class RoutingStatus(str, Enum):
    """Possible outcomes of NL routing attempt."""
    OK = "ok"
    NEEDS_CLARIFICATION = "needs_clarification"
    UNANSWERABLE = "unanswerable"
    ERROR = "error"


@dataclass
class RoutingResult:
    """Result of an NL routing attempt."""
    status: RoutingStatus
    intent_id: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    missing_params: Optional[List[str]] = None
    ambiguity: Optional[Dict[str, Any]] = None
    user_message: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class IntentRegistry:
    """Loads and provides access to the canonical intent registry."""

    def __init__(self, registry_path: str = "app/intent_registry.json"):
        """Load intent registry from JSON file."""
        with open(registry_path, "r") as f:
            registry_data = json.load(f)

        self.version = registry_data["registry_version"]
        self.intents = registry_data["intents"]
        self._intent_map = {intent["intent_id"]: intent for intent in self.intents}

    def get_intent(self, intent_id: str) -> Optional[Dict[str, Any]]:
        """Get intent definition by ID."""
        return self._intent_map.get(intent_id)

    def get_all_intents(self) -> List[Dict[str, Any]]:
        """Get all intent definitions."""
        return self.intents


class NLRouter:
    """Routes natural language questions to deterministic intents using LLM."""

    def __init__(self, registry: IntentRegistry, openai_client: OpenAI):
        """Initialize router with intent registry and OpenAI client."""
        self.registry = registry
        self.client = openai_client
        self.model = "gpt-4o-mini"

    def route(
        self,
        question: str,
        session_context: Optional[Dict[str, Any]] = None,
        is_clarification: bool = False
    ) -> RoutingResult:
        """Route a natural language question to an intent.

        Args:
            question: User's natural language question
            session_context: Optional context (e.g., production_code)
            is_clarification: Whether this is a second-pass clarification attempt

        Returns:
            RoutingResult with status and routing details
        """
        # Build routing prompt
        prompt = self._build_routing_prompt(question, session_context)

        try:
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an intent router. You must respond ONLY with valid JSON matching the required schema. Never include explanations, apologies, or any text outside the JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )

            # Parse LLM response
            response_text = response.choices[0].message.content
            if not response_text:
                return RoutingResult(
                    status=RoutingStatus.ERROR,
                    error_code="llm_empty_response",
                    error_message="LLM returned empty response"
                )

            llm_output = json.loads(response_text)

            # Validate response schema
            if not self._validate_llm_response(llm_output):
                return RoutingResult(
                    status=RoutingStatus.UNANSWERABLE,
                    error_code="invalid_llm_schema",
                    error_message="LLM response did not match required schema"
                )

            # Extract fields
            intent_id = llm_output.get("intent_id")
            confidence = llm_output.get("confidence", 0.0)
            params = llm_output.get("params", {})
            missing_params = llm_output.get("missing_params", [])
            ambiguity = llm_output.get("ambiguity")
            user_message = llm_output.get("user_message")

            # Validate intent_id exists in registry
            if intent_id and not self.registry.get_intent(intent_id):
                return RoutingResult(
                    status=RoutingStatus.UNANSWERABLE,
                    error_code="invalid_intent_id",
                    error_message=f"LLM returned invalid intent_id: {intent_id}"
                )

            # Validate parameters against intent schema
            if intent_id:
                validation_error = self._validate_params(intent_id, params)
                if validation_error:
                    return RoutingResult(
                        status=RoutingStatus.UNANSWERABLE,
                        error_code="invalid_params",
                        error_message=validation_error
                    )

            # Apply confidence gating per Appendix G
            result = self._apply_confidence_gates(
                intent_id=intent_id,
                confidence=confidence,
                params=params,
                missing_params=missing_params,
                ambiguity=ambiguity,
                user_message=user_message,
                is_clarification=is_clarification
            )

            return result

        except json.JSONDecodeError as e:
            return RoutingResult(
                status=RoutingStatus.UNANSWERABLE,
                error_code="llm_invalid_json",
                error_message=f"LLM response was not valid JSON: {str(e)}"
            )
        except Exception as e:
            return RoutingResult(
                status=RoutingStatus.ERROR,
                error_code="routing_error",
                error_message=str(e)
            )

    def _build_routing_prompt(
        self,
        question: str,
        session_context: Optional[Dict[str, Any]]
    ) -> str:
        """Build the LLM routing prompt with intent allowlist and constraints."""
        intents_json = json.dumps(self.registry.get_all_intents(), indent=2)

        context_str = ""
        if session_context:
            context_str = f"\n\nSession context:\n{json.dumps(session_context, indent=2)}"

        prompt = f"""You are a deterministic intent router for a production lineage system.

Your ONLY job is to:
1. Select ONE intent from the allowed list
2. Extract parameters from the user's question
3. Signal uncertainty if needed

ALLOWED INTENTS:
{intents_json}

USER QUESTION:
{question}{context_str}

STRICT RULES:
- You MUST return JSON only (no prose, no explanations)
- You MUST NOT generate SQL
- You MUST NOT claim you executed anything
- You MUST NOT invent parameter values
- If a required parameter is missing, list it in missing_params
- If multiple intents could match, populate ambiguity
- If you're unsure, report lower confidence

REQUIRED OUTPUT SCHEMA:
{{
  "intent_id": "string or null",
  "confidence": 0.0 to 1.0,
  "params": {{}},
  "missing_params": [],
  "ambiguity": null or {{"candidates": ["intent_id1", "intent_id2"]}},
  "user_message": "null or single clarifying question for user"
}}

PARAMETER EXTRACTION EXAMPLES:
- "shot 011_021" → {{"shot_code": "011_021"}}
- "production EXFTR" → {{"production_code": "EXFTR"}}
- UUID strings → {{"package_id": "uuid-value"}}

CONFIDENCE GUIDELINES:
- 0.95+: Perfect match, all required params extracted
- 0.80-0.94: Clear intent, all params present
- 0.60-0.79: Likely intent but missing params or slight ambiguity
- <0.60: Highly uncertain or unsupported

Return JSON now:"""

        return prompt

    def _validate_llm_response(self, llm_output: Dict[str, Any]) -> bool:
        """Validate LLM response matches required schema."""
        required_keys = {"intent_id", "confidence", "params", "missing_params", "ambiguity", "user_message"}
        return required_keys.issubset(llm_output.keys())

    def _validate_params(self, intent_id: str, params: Dict[str, Any]) -> Optional[str]:
        """Validate parameters against intent schema.

        Returns:
            Error message if validation fails, None if valid
        """
        intent = self.registry.get_intent(intent_id)
        if not intent:
            return f"Intent {intent_id} not found in registry"

        required_params = intent.get("required_params", {})

        # Check for required params
        for param_name, param_spec in required_params.items():
            if param_name not in params:
                # This is expected to be caught by missing_params, not an error here
                continue

            # Validate type
            param_value = params[param_name]
            expected_type = param_spec.get("type")

            if expected_type == "string" and not isinstance(param_value, str):
                return f"Parameter {param_name} must be a string"

            # Validate pattern if present
            pattern = param_spec.get("pattern")
            if pattern and isinstance(param_value, str):
                if not re.match(pattern, param_value):
                    return f"Parameter {param_name} does not match required pattern {pattern}"

        return None

    def _apply_confidence_gates(
        self,
        intent_id: Optional[str],
        confidence: float,
        params: Dict[str, Any],
        missing_params: List[str],
        ambiguity: Optional[Dict[str, Any]],
        user_message: Optional[str],
        is_clarification: bool
    ) -> RoutingResult:
        """Apply confidence gating logic per Appendix G.

        Gating order:
        1. If confidence >= ASK_NL_CONFIDENCE_MIN, no ambiguity, no missing required params → OK
        2. Else if first attempt, confidence >= ASK_NL_CONFIDENCE_CLARIFY_MIN, potentially resolvable → NEEDS_CLARIFICATION
        3. Else → UNANSWERABLE

        Second attempt MUST resolve to OK or UNANSWERABLE (no clarification).
        """
        # Check if we have a valid intent
        if not intent_id:
            if not is_clarification and confidence >= settings.ask_nl_confidence_clarify_min:
                return RoutingResult(
                    status=RoutingStatus.NEEDS_CLARIFICATION,
                    confidence=confidence,
                    user_message=user_message or "I couldn't identify a specific question type. Could you rephrase or choose from the supported questions?"
                )
            return RoutingResult(
                status=RoutingStatus.UNANSWERABLE,
                error_code="unsupported_question",
                error_message="Could not map question to a supported intent"
            )

        # Get intent definition to check required params
        intent = self.registry.get_intent(intent_id)
        if not intent:
            return RoutingResult(
                status=RoutingStatus.UNANSWERABLE,
                error_code="invalid_intent",
                error_message=f"Intent {intent_id} not found"
            )

        # Check if required params are present
        required_param_names = list(intent.get("required_params", {}).keys())
        actual_missing = [p for p in required_param_names if p not in params]

        # High confidence, no ambiguity, all required params → executable
        if (
            confidence >= settings.ask_nl_confidence_min
            and not ambiguity
            and not actual_missing
        ):
            return RoutingResult(
                status=RoutingStatus.OK,
                intent_id=intent_id,
                params=params,
                confidence=confidence
            )

        # First attempt, medium confidence, potentially resolvable → clarify
        if (
            not is_clarification
            and confidence >= settings.ask_nl_confidence_clarify_min
            and (actual_missing or ambiguity)
        ):
            # Generate clarification message if none provided
            if not user_message:
                if actual_missing:
                    user_message = f"To answer this question, I need: {', '.join(actual_missing)}. Can you provide this information?"
                elif ambiguity:
                    candidates = ambiguity.get("candidates", [])
                    user_message = f"Your question could mean multiple things. Did you mean: {', '.join(candidates)}?"

            return RoutingResult(
                status=RoutingStatus.NEEDS_CLARIFICATION,
                intent_id=intent_id,
                params=params,
                confidence=confidence,
                missing_params=actual_missing,
                ambiguity=ambiguity,
                user_message=user_message
            )

        # All other cases → unanswerable
        return RoutingResult(
            status=RoutingStatus.UNANSWERABLE,
            error_code="low_confidence" if confidence < settings.ask_nl_confidence_clarify_min else "missing_required_params",
            error_message=f"Cannot execute query (confidence: {confidence:.2f}, missing: {actual_missing})"
        )


# Module-level instances (initialized lazily)
_registry: Optional[IntentRegistry] = None
_router: Optional[NLRouter] = None


def get_router() -> Optional[NLRouter]:
    """Get the global NLRouter instance, or None if NL is disabled."""
    global _registry, _router

    if not settings.is_nl_enabled():
        return None

    if _router is None:
        # Initialize registry and router
        _registry = IntentRegistry()
        openai_client = OpenAI(api_key=settings.openai_api_key)
        _router = NLRouter(_registry, openai_client)

    return _router
