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
import logging
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI
from app.config import settings
import anyio

# Hard timeout for LLM calls (application-level guard)
LLM_TIMEOUT_SECONDS = 12.0

logger = logging.getLogger(__name__)
uvicorn_logger = logging.getLogger("uvicorn.error")


# Mapping of intent_id to user-facing plain English descriptions for clarification messages
# These descriptions must NOT include: "intent", "intent_id", "registry", "confidence", "threshold"
INTENT_USER_FACING_DESCRIPTIONS: Dict[str, str] = {
    "latest_camera_original": "checking the latest camera original",
    "lineage_chain_to_latest_edit_export": "tracing the lineage chain to the latest edit export",
    "shots_with_dailies_no_edit_export": "finding shots with dailies but no edit export",
    "shots_ready_for_turnover_and_missing": "finding shots ready for turnover but not delivered",
    "package_members": "listing package members",
    "source_relink_keys": "getting source relink keys",
    "latest_versions_by_type": "checking latest versions by type",
    "archive_status": "checking archive status"
}


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


def _trace(trace_id: str, stage: str, payload: Dict[str, Any]) -> None:
    """Emit trace log if ASK_NL_TRACE is enabled.

    Args:
        trace_id: Unique trace identifier for this request
        stage: Stage name (e.g., "nl_request_received")
        payload: Additional data to log
    """
    if not settings.ask_nl_trace:
        return

    log_entry = {
        "trace_id": trace_id,
        "stage": stage,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **payload
    }
    uvicorn_logger.info(json.dumps(log_entry))


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
        # Generate trace ID for this request
        trace_id = str(uuid.uuid4())

        # Stage 1: nl_request_received
        _trace(trace_id, "nl_request_received", {
            "question": question,
            "is_clarification": is_clarification,
            "production_code": session_context.get("production_code") if session_context else None,
            "mode": "nl"
        })

        # Stage 2: nl_registry_loaded
        candidate_intents = [
            {
                "intent_id": intent["intent_id"],
                "title": intent.get("title"),
                "description": intent.get("description")
            }
            for intent in self.registry.get_all_intents()
        ]
        _trace(trace_id, "nl_registry_loaded", {
            "registry_version": self.registry.version,
            "candidate_intents": candidate_intents
        })

        # Handle deterministic ambiguity resolution for clarification attempts
        if is_clarification and session_context:
            clarification_kind = session_context.get("clarification_kind")
            ambiguity_candidates = session_context.get("ambiguity_candidates")

            if clarification_kind == "ambiguity" and isinstance(ambiguity_candidates, list) and len(ambiguity_candidates) > 0:
                # Deterministic resolution - skip LLM call
                resolution_result = self._resolve_ambiguity_deterministically(
                    trace_id=trace_id,
                    user_reply=question,
                    ambiguity_candidates=ambiguity_candidates,
                    session_context=session_context
                )
                if resolution_result:
                    return resolution_result

        # Build routing prompt
        prompt = self._build_routing_prompt(question, session_context)

        # Stage 3: nl_prompt_built
        prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
        prompt_preview = prompt[:1200]
        if len(prompt) > 1200:
            prompt_preview += "...<truncated>"

        _trace(trace_id, "nl_prompt_built", {
            "model": self.model,
            "temperature": 0.0,
            "max_tokens": None,
            "prompt_preview": prompt_preview,
            "prompt_len_chars": len(prompt),
            "prompt_hash": prompt_hash
        })

        try:
            # Call LLM with application-level timeout guard (belt + suspenders)
            # Run synchronous OpenAI call in thread with anyio timeout enforcement
            async def _call_llm_with_timeout():
                with anyio.fail_after(LLM_TIMEOUT_SECONDS):
                    # Run synchronous OpenAI call in thread
                    return await anyio.to_thread.run_sync(
                        lambda: self.client.chat.completions.create(
                            model=self.model,
                            messages=[
                                {"role": "system", "content": "You are an intent router. You must respond ONLY with valid JSON matching the required schema. Never include explanations, apologies, or any text outside the JSON."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.0,
                            response_format={"type": "json_object"}
                        ),
                        abandon_on_cancel=True
                    )

            response = anyio.run(_call_llm_with_timeout)

            # Parse LLM response
            response_text = response.choices[0].message.content
            if not response_text:
                return RoutingResult(
                    status=RoutingStatus.ERROR,
                    error_code="llm_empty_response",
                    error_message="LLM returned empty response"
                )

            # Stage 4: nl_openai_raw_response
            raw_preview = response_text[:1200]
            if len(response_text) > 1200:
                raw_preview += "...<truncated>"

            _trace(trace_id, "nl_openai_raw_response", {
                "raw_preview": raw_preview,
                "raw_len_chars": len(response_text)
            })

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

            # Stage 5: nl_openai_parsed
            # Log LLM's original user_message for trace/debugging, but note it won't be used verbatim
            # needs_clarification must match has_clarification_signal logic (including user_message-only signal)
            has_clarification_signal_parsed = bool(missing_params or ambiguity or (user_message and not intent_id))
            _trace(trace_id, "nl_openai_parsed", {
                "intent_id": intent_id,
                "confidence": confidence,
                "missing_params": missing_params,
                "needs_clarification": has_clarification_signal_parsed,
                "llm_user_message": user_message,  # LLM's original message (for trace only)
                "ambiguity_candidates": ambiguity.get("candidates") if ambiguity else None
            })

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

            # Handle clarification attempts: check if user is confirming/rejecting a previous confirmation request
            if is_clarification and session_context:
                previous_intent_id = session_context.get("intent_id")
                if previous_intent_id and isinstance(previous_intent_id, str):
                    # Check if user's question is a confirmation or rejection
                    confirmation_result = self._check_confirmation_response(
                        question, previous_intent_id, session_context, intent_id, params
                    )
                    if confirmation_result:
                        return confirmation_result

            # Apply confidence gating per Appendix G
            result = self._apply_confidence_gates(
                trace_id=trace_id,
                question=question,
                intent_id=intent_id,
                confidence=confidence,
                params=params,
                missing_params=missing_params,
                ambiguity=ambiguity,
                user_message=user_message,
                is_clarification=is_clarification,
                session_context=session_context
            )

            return result

        except TimeoutError as e:
            # Application-level timeout (anyio.fail_after) or network timeout
            return RoutingResult(
                status=RoutingStatus.ERROR,
                error_code="llm_timeout",
                error_message=f"LLM request timed out after {LLM_TIMEOUT_SECONDS} seconds"
            )
        except OSError as e:
            # Connection error during LLM call
            return RoutingResult(
                status=RoutingStatus.ERROR,
                error_code="llm_timeout",
                error_message=f"LLM request connection failed: {str(e)}"
            )
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
- If EXACTLY ONE intent matches the question's goal but parameters are missing:
  * Set intent_id to that intent
  * List missing parameters in missing_params
  * Set user_message to null (MUST be JSON null, not a string)
  * Set confidence based on clarity (0.60-0.79 typical)
- If MULTIPLE intents could match (true ambiguity):
  * Set intent_id to null
  * Set ambiguity to {{"candidates": ["intent_id1", "intent_id2", "intent_id3"]}} (top 2-3 candidate intent IDs)
  * Set user_message to null (MUST be JSON null, not a string)
  * Set confidence based on uncertainty
- If NO intent matches:
  * Set intent_id to null
  * Set confidence low (<0.60)
  * Set user_message to explain why

REQUIRED OUTPUT SCHEMA:
{{
  "intent_id": "string or null",
  "confidence": 0.0 to 1.0,
  "params": {{}},
  "missing_params": [],
  "ambiguity": null or {{"candidates": ["intent_id1", "intent_id2", "intent_id3"]}},
    "user_message": "string or null"
}}

IMPORTANT: For missing_params or ambiguity cases, user_message MUST be null (not a string).
The server will generate clarification messages deterministically from your response.

PARAMETER EXTRACTION EXAMPLES:
- "shot 011_002" → {{"shot_code": "011_002"}}
- "production EXFTR" → {{"production_code": "EXFTR"}}
- UUID strings → {{"package_id": "uuid-value"}}

CONFIDENCE GUIDELINES:
- 0.95+: Perfect match, all required params extracted
- 0.80-0.94: Clear intent, all params present
- 0.60-0.79: Clear intent but missing params, or slight ambiguity
- <0.60: Highly uncertain, multiple intents possible, or unsupported

Return JSON now:"""

        return prompt

    def _validate_llm_response(self, llm_output: Dict[str, Any]) -> bool:
        """Validate LLM response matches required schema."""
        required_keys = {"intent_id", "confidence", "params", "missing_params", "ambiguity", "user_message"}
        return required_keys.issubset(llm_output.keys())

    def _get_intent_user_facing_description(self, intent_id: str) -> str:
        """Get user-facing description for an intent_id with fallback to registry.

        Args:
            intent_id: The intent identifier

        Returns:
            Plain English description, sanitized to avoid internal terminology
        """
        # First try the explicit mapping
        if intent_id in INTENT_USER_FACING_DESCRIPTIONS:
            return INTENT_USER_FACING_DESCRIPTIONS[intent_id]

        # Fallback to intent registry (title preferred, else description)
        intent = self.registry.get_intent(intent_id)
        if intent:
            # Prefer title, fallback to description
            desc = intent.get("title") or intent.get("description", "")
            if desc:
                # Sanitize: remove internal terminology
                sanitized = desc.lower()
                forbidden_terms = ["intent", "intent_id", "registry", "confidence", "threshold"]
                for term in forbidden_terms:
                    sanitized = sanitized.replace(term, "")
                # Clean up extra spaces and return
                sanitized = " ".join(sanitized.split())
                if sanitized:
                    return sanitized

        # Ultimate fallback
        return "answering your question"

    def _normalize_ambiguity_candidates(self, candidates: Any) -> List[str]:
        """Normalize and validate ambiguity candidates list.

        Handles both string lists and object lists with {"intent_id": "..."} format.

        Args:
            candidates: Raw candidates from LLM (list of strings or list of objects)

        Returns:
            Normalized list of intent_id strings
        """
        if not isinstance(candidates, list):
            return []

        normalized = []
        for item in candidates:
            if isinstance(item, str):
                normalized.append(item)
            elif isinstance(item, dict) and "intent_id" in item:
                intent_id = item["intent_id"]
                if isinstance(intent_id, str):
                    normalized.append(intent_id)

        return normalized

    def _generate_clarification_message(
        self,
        intent_id: Optional[str],
        ambiguity: Optional[Dict[str, Any]],
        missing_params: List[str],
        params: Dict[str, Any]
    ) -> str:
        """Generate deterministic user-facing clarification message.

        This method ensures clarification messages:
        - Never include internal terminology (intent, intent_id, registry, confidence, threshold)
        - Are generated from a strict whitelist mapping with registry fallback
        - Include shot_code when available
        - Present 2-3 plain-English domain options for ambiguity cases

        Args:
            intent_id: Selected intent ID (if single intent with missing params)
            ambiguity: Ambiguity dict with candidates list (if multiple intents)
            missing_params: List of missing parameter names
            params: Extracted parameters (may include shot_code)

        Returns:
            Plain English clarification message
        """
        shot_code = params.get("shot_code")
        shot_context = f" for shot {shot_code}" if shot_code else ""

        # Case 1: Ambiguity - multiple candidate intents
        if ambiguity:
            raw_candidates = ambiguity.get("candidates", [])
            normalized_candidates = self._normalize_ambiguity_candidates(raw_candidates)

            if normalized_candidates:
                # Limit to top 2-3 candidates for clarity
                candidate_descriptions = []
                for candidate_id in normalized_candidates[:3]:
                    desc = self._get_intent_user_facing_description(candidate_id)
                    if desc and desc != "answering your question":  # Skip ultimate fallback
                        candidate_descriptions.append(desc)

                if candidate_descriptions:
                    # Build numbered list of options
                    numbered_options = []
                    for idx, desc in enumerate(candidate_descriptions, start=1):
                        numbered_options.append(f"{idx}) {desc}")

                    options_text = "\n".join(numbered_options)
                    shot_prefix = f"Which of these do you mean for shot {shot_code}?\n" if shot_code else "Which of these do you mean?\n"
                    message = f"{shot_prefix}{options_text}\nReply with {', '.join(str(i) for i in range(1, len(candidate_descriptions) + 1))} or describe your choice."
                    return message

        # Case 2: Single intent but missing required parameters
        if intent_id and missing_params:
            intent_desc = self._get_intent_user_facing_description(intent_id)
            # Convert parameter names to user-friendly terms
            param_descriptions = []
            for param in missing_params:
                if param == "shot_code":
                    param_descriptions.append("a shot code")
                elif param == "production_code":
                    param_descriptions.append("a production code")
                elif param == "package_id":
                    param_descriptions.append("a package ID")
                else:
                    param_descriptions.append(param.replace("_", " "))

            if len(param_descriptions) == 1:
                return f"To {intent_desc}{shot_context}, I need {param_descriptions[0]}. Can you provide it?"
            else:
                return f"To {intent_desc}{shot_context}, I need {', '.join(param_descriptions[:-1])}, and {param_descriptions[-1]}. Can you provide this information?"

        # Case 3: Fallback for other clarification needs
        if shot_code:
            return f"Could you provide more details about what you'd like to know about shot {shot_code}?"
        return "Could you provide more details or rephrase your question?"

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

    def _resolve_ambiguity_deterministically(
        self,
        trace_id: str,
        user_reply: str,
        ambiguity_candidates: List[str],
        session_context: Dict[str, Any]
    ) -> Optional[RoutingResult]:
        """Resolve ambiguity deterministically from user clarification.

        Supports numeric selection (1, 2, 3) and free-text keyword matching.

        Args:
            trace_id: Trace ID for logging
            user_reply: User's clarification text
            ambiguity_candidates: Ordered list of intent_ids from prior clarification
            session_context: Session context containing original_question

        Returns:
            RoutingResult if resolution succeeds, None if should fall through to normal routing
        """
        # Defensively strip original_question prefix if present
        user_reply_clean = user_reply.strip()
        original_question = session_context.get("original_question", "")
        if isinstance(original_question, str) and user_reply_clean.startswith(original_question):
            user_reply_clean = user_reply_clean[len(original_question):].strip()

        selected_intent_id = None
        selection_mode = None
        keyword_scores = None

        # Method 1: Numeric selection
        numeric_match = re.match(r'^\s*(\d+)\s*$', user_reply_clean)
        if numeric_match:
            try:
                N = int(numeric_match.group(1))
                if 1 <= N <= len(ambiguity_candidates):
                    selected_intent_id = ambiguity_candidates[N - 1]
                    selection_mode = "index"
                else:
                    _trace(trace_id, "nl_decision", {
                        "routing_status": "unanswerable",
                        "reason": "deterministic_ambiguity_resolution: numeric choice out of range",
                        "deterministic_ambiguity_resolution": True,
                        "selection_mode": "index",
                        "choice": N,
                        "candidates_count": len(ambiguity_candidates)
                    })
                    return RoutingResult(
                        status=RoutingStatus.UNANSWERABLE,
                        error_code="clarification_choice_out_of_range",
                        error_message=f"Please choose a number between 1 and {len(ambiguity_candidates)}."
                    )
            except (ValueError, IndexError):
                # Fall through to keyword matching
                pass

        # Method 2: Free-text keyword matching
        if not selected_intent_id:
            # Normalize user reply: lowercase, strip punctuation, split on whitespace
            normalized_reply = re.sub(r'[^\w\s]', ' ', user_reply_clean.lower())
            user_tokens = set(normalized_reply.split())
            user_tokens.discard('')  # Remove empty strings

            if not user_tokens:
                # Empty or only punctuation - cannot resolve
                _trace(trace_id, "nl_decision", {
                    "routing_status": "unanswerable",
                    "reason": "deterministic_ambiguity_resolution: no meaningful tokens",
                    "deterministic_ambiguity_resolution": True,
                    "selection_mode": "keywords"
                })
                return RoutingResult(
                    status=RoutingStatus.UNANSWERABLE,
                    error_code="ambiguous_clarification_unresolved",
                    error_message="Please provide more specific clarification."
                )

            # Score each candidate
            scores = []
            for candidate_id in ambiguity_candidates:
                intent = self.registry.get_intent(candidate_id)
                if not intent:
                    continue

                # Combine title and description for matching
                title = (intent.get("title") or "").lower()
                description = (intent.get("description") or "").lower()
                combined_text = f"{title} {description}"

                # Count matching tokens
                score = sum(1 for token in user_tokens if token in combined_text)
                scores.append((candidate_id, score))

            keyword_scores = {candidate_id: score for candidate_id, score in scores}

            # Sort by score descending
            scores.sort(key=lambda x: x[1], reverse=True)

            if len(scores) == 0:
                _trace(trace_id, "nl_decision", {
                    "routing_status": "unanswerable",
                    "reason": "deterministic_ambiguity_resolution: no valid candidates",
                    "deterministic_ambiguity_resolution": True,
                    "selection_mode": "keywords"
                })
                return RoutingResult(
                    status=RoutingStatus.UNANSWERABLE,
                    error_code="ambiguous_clarification_unresolved",
                    error_message="Unable to match your clarification to any option."
                )

            top_score = scores[0][1]
            second_score = scores[1][1] if len(scores) > 1 else 0

            # Select winner only if top_score > 0 and strictly greater than second
            if top_score > 0 and top_score > second_score:
                selected_intent_id = scores[0][0]
                selection_mode = "keywords"
            else:
                _trace(trace_id, "nl_decision", {
                    "routing_status": "unanswerable",
                    "reason": "deterministic_ambiguity_resolution: no clear winner",
                    "deterministic_ambiguity_resolution": True,
                    "selection_mode": "keywords",
                    "keyword_scores": keyword_scores
                })
                return RoutingResult(
                    status=RoutingStatus.UNANSWERABLE,
                    error_code="ambiguous_clarification_unresolved",
                    error_message="Your clarification matches multiple options. Please be more specific or use a number (1, 2, 3)."
                )

        # Validate selected intent exists
        if not selected_intent_id or not self.registry.get_intent(selected_intent_id):
            _trace(trace_id, "nl_decision", {
                "routing_status": "unanswerable",
                "reason": "deterministic_ambiguity_resolution: selected intent not found",
                "deterministic_ambiguity_resolution": True,
                "selection_mode": selection_mode,
                "selected_intent_id": selected_intent_id
            })
            return RoutingResult(
                status=RoutingStatus.UNANSWERABLE,
                error_code="invalid_intent_selection",
                error_message="Selected intent is not available."
            )

        # Extract params from original_question if available
        params = {}
        original_question = session_context.get("original_question", "")
        if isinstance(original_question, str):
            # Extract shot_code if present
            shot_match = re.search(r'(\d{3}_\d{3})', original_question)
            if shot_match:
                params["shot_code"] = shot_match.group(1)

        # Validate required params
        intent = self.registry.get_intent(selected_intent_id)
        if intent:
            required_param_names = list(intent.get("required_params", {}).keys())
            missing_required = [p for p in required_param_names if p not in params]

            if missing_required:
                _trace(trace_id, "nl_decision", {
                    "routing_status": "unanswerable",
                    "reason": "deterministic_ambiguity_resolution: missing required params",
                    "deterministic_ambiguity_resolution": True,
                    "selection_mode": selection_mode,
                    "selected_intent_id": selected_intent_id,
                    "missing_params": missing_required
                })
                return RoutingResult(
                    status=RoutingStatus.UNANSWERABLE,
                    error_code="missing_params_after_clarification",
                    error_message=f"Missing required information: {', '.join(missing_required)}."
                )

            # Validate params against schema
            validation_error = self._validate_params(selected_intent_id, params)
            if validation_error:
                _trace(trace_id, "nl_decision", {
                    "routing_status": "unanswerable",
                    "reason": "deterministic_ambiguity_resolution: params validation failed",
                    "deterministic_ambiguity_resolution": True,
                    "selection_mode": selection_mode,
                    "selected_intent_id": selected_intent_id,
                    "validation_error": validation_error
                })
                return RoutingResult(
                    status=RoutingStatus.UNANSWERABLE,
                    error_code="invalid_params_after_clarification",
                    error_message="Invalid parameters for selected option."
                )

        # Success - return OK with confidence=1.0 (bypasses all confidence gates)
        _trace(trace_id, "nl_decision", {
            "routing_status": "ok",
            "reason": "deterministic_ambiguity_resolution: resolved successfully",
            "deterministic_ambiguity_resolution": True,
            "selection_mode": selection_mode,
            "selected_intent_id": selected_intent_id,
            "keyword_scores": keyword_scores,
            "confidence": 1.0
        })
        return RoutingResult(
            status=RoutingStatus.OK,
            intent_id=selected_intent_id,
            params=params,
            confidence=1.0  # High confidence for deterministic resolution
        )

    def _check_confirmation_response(
        self,
        question: str,
        previous_intent_id: str,
        session_context: Dict[str, Any],
        current_intent_id: Optional[str],
        current_params: Dict[str, Any]
    ) -> Optional[RoutingResult]:
        """Check if user's question is a confirmation or rejection of a previous confirmation request.

        Args:
            question: User's response to confirmation prompt
            previous_intent_id: Intent ID from previous clarification request
            session_context: Session context containing previous params if available
            current_intent_id: Intent ID from current LLM response (may be None for short confirmations)
            current_params: Params from current LLM response

        Returns:
            RoutingResult if confirmation/rejection detected, None otherwise
        """
        # Normalize: lowercase, strip whitespace, remove surrounding punctuation
        normalized = question.strip().lower()
        # Remove leading/trailing punctuation but keep internal punctuation
        normalized = normalized.strip('.,!?;:')

        # Split into words for exact matching
        words = normalized.split()

        # Only process short responses (<= 3 words)
        if len(words) > 3:
            return None

        # Exact token matches for confirmation
        confirmation_tokens = {"y", "yes", "ok", "okay", "sure"}
        confirmation_phrases = {"run it", "do it", "go ahead", "proceed", "execute"}

        # Exact token matches for rejection
        rejection_tokens = {"n", "no", "nope", "wrong", "different", "cancel", "stop"}

        # Check for exact matches
        is_confirmation = False
        is_rejection = False

        # Check token matches
        for word in words:
            if word in confirmation_tokens:
                is_confirmation = True
            if word in rejection_tokens:
                is_rejection = True

        # Check phrase matches (exact phrase in normalized string)
        normalized_phrase = " ".join(words)
        if normalized_phrase in confirmation_phrases:
            is_confirmation = True

        # If both appear, treat as neither and fall through
        if is_confirmation and is_rejection:
            return None

        if is_confirmation:
            # User confirmed - execute the previous intent
            # Use params from current LLM response if available, otherwise try to extract from original question
            confirmed_params = current_params.copy() if current_params else {}

            # If params are missing and we have original_question, try to extract shot_code from it
            if not confirmed_params.get("shot_code") and "original_question" in session_context:
                original_question = session_context.get("original_question")
                if isinstance(original_question, str):
                    # Simple extraction: look for shot_code pattern
                    shot_match = re.search(r'(\d{3}_\d{3})', original_question)
                    if shot_match:
                        confirmed_params["shot_code"] = shot_match.group(1)

            # Validate required params before returning OK
            intent = self.registry.get_intent(previous_intent_id)
            if intent:
                required_param_names = list(intent.get("required_params", {}).keys())
                missing_required = [p for p in required_param_names if p not in confirmed_params]

                if missing_required:
                    # Check if shot_code is missing (most common case)
                    if "shot_code" in missing_required:
                        return RoutingResult(
                            status=RoutingStatus.UNANSWERABLE,
                            error_code="missing_required_params_after_confirmation",
                            error_message="Please re-ask your question and include the shot code (e.g., 011_002)."
                        )
                    else:
                        return RoutingResult(
                            status=RoutingStatus.UNANSWERABLE,
                            error_code="missing_required_params_after_confirmation",
                            error_message="Please re-ask your question with all required information."
                        )

                # Validate params against schema
                validation_error = self._validate_params(previous_intent_id, confirmed_params)
                if validation_error:
                    return RoutingResult(
                        status=RoutingStatus.UNANSWERABLE,
                        error_code="invalid_params_after_confirmation",
                        error_message="Please re-ask your question with valid parameters."
                    )

            # Return OK to execute the intent (confidence check bypassed for confirmation)
            return RoutingResult(
                status=RoutingStatus.OK,
                intent_id=previous_intent_id,
                params=confirmed_params,
                confidence=1.0  # High confidence for user-confirmed execution
            )
        elif is_rejection:
            # User rejected - return UNANSWERABLE
            return RoutingResult(
                status=RoutingStatus.UNANSWERABLE,
                error_code="user_rejected_confirmation",
                error_message="Please rephrase your question or choose from the supported questions."
            )

        # Not a clear confirmation/rejection - return None to continue normal routing
        return None

    def _apply_confidence_gates(
        self,
        trace_id: str,
        question: str,
        intent_id: Optional[str],
        confidence: float,
        params: Dict[str, Any],
        missing_params: List[str],
        ambiguity: Optional[Dict[str, Any]],
        user_message: Optional[str],
        is_clarification: bool,
        session_context: Optional[Dict[str, Any]] = None
    ) -> RoutingResult:
        """Apply confidence gating logic per Appendix G.

        Gating order:
        1. First attempt: Check if clarification is possible (missing_params, ambiguity, or user_message present)
           → If yes and confidence reasonable, return NEEDS_CLARIFICATION
        2. Second attempt (is_clarification=True): If still needs clarification → UNANSWERABLE (no loops)
        3. If confidence >= ASK_NL_CONFIDENCE_MIN, no ambiguity, no missing required params → OK
        4. Else → UNANSWERABLE

        Second attempt MUST resolve to OK or UNANSWERABLE (no clarification loops).
        """
        # Detect if LLM is signaling that clarification would help
        has_clarification_signal = bool(missing_params or ambiguity or (user_message and not intent_id))

        # GUARD: If this is a clarification attempt and still needs clarification → UNANSWERABLE (no loops)
        if is_clarification and has_clarification_signal:
            _trace(trace_id, "nl_decision", {
                "routing_status": "unanswerable",
                "reason": "clarification attempt still requires clarification (max 1 cycle per Appendix G)",
                "confidence": confidence,
                "missing_params": missing_params,
                "has_ambiguity": bool(ambiguity),
                "intent_id": intent_id
            })
            return RoutingResult(
                status=RoutingStatus.UNANSWERABLE,
                error_code="clarification_loop_prevented",
                error_message="Unable to resolve question after clarification attempt"
            )

        # Get intent definition to validate (if intent_id provided)
        intent = None
        actual_missing = []
        if intent_id:
            intent = self.registry.get_intent(intent_id)
            if not intent:
                _trace(trace_id, "nl_decision", {
                    "routing_status": "unanswerable",
                    "reason": "invalid intent_id from LLM",
                    "intent_id": intent_id
                })
                return RoutingResult(
                    status=RoutingStatus.UNANSWERABLE,
                    error_code="invalid_intent",
                    error_message=f"Intent {intent_id} not found in registry"
                )

            # Check if required params are present
            required_param_names = list(intent.get("required_params", {}).keys())
            actual_missing = [p for p in required_param_names if p not in params]

        # PATH 1: First attempt with clarification signal → NEEDS_CLARIFICATION
        # This handles missing params, ambiguity, or other resolvable uncertainty
        # Return NEEDS_CLARIFICATION if missing_params OR ambiguity.candidates present (regardless of confidence)
        if not is_clarification and has_clarification_signal:
            # Check for missing_params or ambiguity.candidates (expected workflow outcomes)
            has_missing_params = bool(actual_missing if intent_id else missing_params)
            has_ambiguity_candidates = False
            normalized_candidates = None
            if ambiguity:
                raw_candidates = ambiguity.get("candidates", [])
                normalized_candidates = self._normalize_ambiguity_candidates(raw_candidates)
                has_ambiguity_candidates = bool(normalized_candidates)
                # Update ambiguity dict with normalized candidates
                if normalized_candidates:
                    ambiguity = {"candidates": normalized_candidates}
                else:
                    # Empty candidates list - fall back to generic clarification
                    ambiguity = None

            # If missing_params or ambiguity.candidates, always return NEEDS_CLARIFICATION (expected outcome)
            # This is an expected workflow state, not an error, so we clarify regardless of confidence
            if has_missing_params or has_ambiguity_candidates:
                # ALWAYS generate clarification message deterministically from router
                # DO NOT use LLM-provided user_message verbatim (per Appendix G requirements)
                llm_original_message = user_message  # Preserve for trace logging
                router_generated_message = self._generate_clarification_message(
                    intent_id=intent_id,
                    ambiguity=ambiguity,
                    missing_params=actual_missing if intent_id else missing_params,
                    params=params
                )

                _trace(trace_id, "nl_decision", {
                    "routing_status": "needs_clarification",
                    "reason": "first attempt with missing params or ambiguity candidates (expected workflow outcome)",
                    "confidence": confidence,
                    "missing_params": actual_missing if intent_id else missing_params,
                    "has_ambiguity": bool(ambiguity),
                    "intent_id": intent_id,
                    "normalized_ambiguity_candidates": normalized_candidates if normalized_candidates else None,
                    "llm_user_message": llm_original_message,  # LLM's original message (for trace only)
                    "router_generated_message": router_generated_message  # Router-generated message (used in response)
                })

                # Prepare session_context for ambiguity-based clarification
                # Note: The frontend will receive this and should store it for the next request
                # We include ambiguity info in the response for frontend to use
                result_ambiguity = ambiguity
                session_context_payload = None
                if has_ambiguity_candidates and normalized_candidates:
                    # Store ambiguity context in the ambiguity dict for frontend to extract
                    result_ambiguity = {
                        "candidates": normalized_candidates,
                        "clarification_kind": "ambiguity",
                        "original_question": question  # Store original question for param extraction
                    }
                    session_context_payload = {
                        "clarification_kind": "ambiguity",
                        "ambiguity_candidates": normalized_candidates,
                        "original_question": question
                    }

                _trace(trace_id, "nl_ambiguity_clarification_payload", {
                    "session_context_payload": session_context_payload,
                    "result_ambiguity": result_ambiguity,
                    "payload_built_successfully": session_context_payload is not None
                })

                return RoutingResult(
                    status=RoutingStatus.NEEDS_CLARIFICATION,
                    intent_id=intent_id,
                    params=params,
                    confidence=confidence,
                    missing_params=actual_missing if intent_id else missing_params,
                    ambiguity=result_ambiguity,
                    user_message=router_generated_message  # Router-generated, deterministic message
                )
            # If neither missing_params nor ambiguity.candidates, fall through to PATH 3 (UNANSWERABLE)

        # PATH 2: Valid intent with high confidence and all params → OK (executable)
        if (
            intent_id
            and intent
            and confidence >= settings.ask_nl_confidence_min
            and not ambiguity
            and not actual_missing
        ):
            _trace(trace_id, "nl_decision", {
                "routing_status": "ok",
                "reason": "confidence >= execute threshold, no ambiguity, all required params present",
                "confidence": confidence,
                "execute_threshold": settings.ask_nl_confidence_min,
                "intent_id": intent_id
            })
            return RoutingResult(
                status=RoutingStatus.OK,
                intent_id=intent_id,
                params=params,
                confidence=confidence
            )

        # PATH 2b: Weak execute - clear intent with all params but lower confidence
        # Only applies when intent is fully specified (no missing params, no ambiguity)
        if (
            intent_id
            and intent
            and confidence >= settings.ask_nl_confidence_execute_weak_min
            and confidence < settings.ask_nl_confidence_min
            and not ambiguity
            and not actual_missing
        ):
            _trace(trace_id, "nl_decision", {
                "routing_status": "ok",
                "reason": "confidence >= weak execute threshold, no ambiguity, all required params present",
                "confidence": confidence,
                "execute_threshold": settings.ask_nl_confidence_min,
                "weak_execute_threshold": settings.ask_nl_confidence_execute_weak_min,
                "intent_id": intent_id
            })
            return RoutingResult(
                status=RoutingStatus.OK,
                intent_id=intent_id,
                params=params,
                confidence=confidence
            )

        # PATH 2c: Single-intent confirmation - fully specified intent but confidence below weak execute threshold
        # Only on first attempt (not clarification)
        if (
            not is_clarification
            and intent_id
            and intent
            and confidence < settings.ask_nl_confidence_execute_weak_min
            and not actual_missing
        ):
            # Check if ambiguity is null/empty or normalizes to empty
            has_ambiguity_candidates = False
            if ambiguity:
                raw_candidates = ambiguity.get("candidates", [])
                normalized_candidates = self._normalize_ambiguity_candidates(raw_candidates)
                has_ambiguity_candidates = bool(normalized_candidates)

            if not has_ambiguity_candidates:
                # Generate confirmation message
                intent_desc = self._get_intent_user_facing_description(intent_id)
                shot_code = params.get("shot_code")
                shot_context = f" for shot {shot_code}" if shot_code else ""
                confirmation_message = f"I can help you with {intent_desc}{shot_context}. Do you want me to run that?"

                _trace(trace_id, "nl_decision", {
                    "routing_status": "needs_clarification",
                    "reason": "low-confidence single intent; asking for confirmation",
                    "confidence": confidence,
                    "weak_execute_threshold": settings.ask_nl_confidence_execute_weak_min,
                    "intent_id": intent_id,
                    "confirmation_required": True
                })
                return RoutingResult(
                    status=RoutingStatus.NEEDS_CLARIFICATION,
                    intent_id=intent_id,
                    params=params,
                    confidence=confidence,
                    missing_params=[],
                    ambiguity=None,
                    user_message=confirmation_message
                )

        # PATH 3: All other cases → UNANSWERABLE
        # This includes: low confidence, no valid intent_id, or missing params on clarification attempt
        if not intent_id:
            reason = "no valid intent identified"
        elif confidence < settings.ask_nl_confidence_execute_weak_min:
            reason = f"confidence {confidence:.2f} below weak execute threshold {settings.ask_nl_confidence_execute_weak_min}"
        elif actual_missing:
            reason = f"missing required params: {actual_missing}"
        else:
            reason = "unable to resolve question"

        if is_clarification:
            reason = f"clarification attempt failed: {reason}"

        _trace(trace_id, "nl_decision", {
            "routing_status": "unanswerable",
            "reason": reason,
            "confidence": confidence,
            "execute_threshold": settings.ask_nl_confidence_min,
            "intent_id": intent_id,
            "is_clarification": is_clarification
        })
        return RoutingResult(
            status=RoutingStatus.UNANSWERABLE,
            error_code="unsupported_question",
            error_message=f"Cannot execute query: {reason}"
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
        # Set timeout for LLM calls to prevent hanging on network issues (belt + suspenders with anyio.fail_after)
        openai_client = OpenAI(api_key=settings.openai_api_key, timeout=LLM_TIMEOUT_SECONDS)
        _router = NLRouter(_registry, openai_client)

    return _router
