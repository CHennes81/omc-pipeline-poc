"""Helpers for providers without a native "JSON mode"."""


def extract_json_text(text: str) -> str:
    """Return the JSON object embedded in a model reply.

    Models sometimes wrap JSON in a markdown code fence or add a stray sentence around it.
    This strips both and returns the outermost ``{...}`` span. If no object is found the
    stripped text is returned unchanged, so the caller's ``json.loads`` reports the real
    problem instead of this helper hiding it.
    """
    stripped = (text or "").strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        lines = lines[1:]  # opening fence, with optional language tag
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end > start:
        return stripped[start : end + 1]
    return stripped
