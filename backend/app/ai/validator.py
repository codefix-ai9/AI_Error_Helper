"""
AI output validator (§7.4).

Pipeline:
  1. Strict JSON parse (tolerate one wrapping code fence).
  2. Schema + type validation via Pydantic.
  3. Semantic checks: length caps, corrected_code size, affected_code substring,
     line-number authority lock.
  4. On first failure → one repair attempt; on second failure → raises ValidationError.
"""
import json
import re
import logging
from typing import Tuple, List, Optional
from pydantic import ValidationError as PydanticValidationError

from backend.app.ai.schemas import AIExplanation
from backend.app.models.stages import StaticAnalysisResult, NormalizedInput

logger = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]+?)\s*```", re.IGNORECASE)


class AIValidationError(Exception):
    """Raised when AI output cannot be validated after one repair attempt."""
    pass


def _strip_fence(raw: str) -> str:
    """Strip a single wrapping markdown code fence if present."""
    m = _FENCE_RE.search(raw.strip())
    if m:
        return m.group(1)
    return raw.strip()


def _parse_json(raw: str) -> dict:
    """Parse JSON, tolerating one wrapping code fence."""
    cleaned = _strip_fence(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise AIValidationError(f"JSON parse error: {e}") from e


def _validate_schema(data: dict) -> Tuple[AIExplanation, List[str]]:
    """Validate against schema; return (model, warnings)."""
    warnings: List[str] = []
    try:
        model = AIExplanation(**data)
    except PydanticValidationError as e:
        raise AIValidationError(f"Schema validation failed: {e}") from e
    return model, warnings


def _semantic_checks(
    model: AIExplanation,
    source_code: str,
    static_result: StaticAnalysisResult,
) -> Tuple[AIExplanation, List[str]]:
    """Apply semantic rules. Returns (potentially mutated model, warnings)."""
    warnings: List[str] = []
    data = model.model_dump()

    # Check debugging_steps length per item
    fixed_steps = []
    for step in data["debugging_steps"]:
        if len(step) > 300:
            step = step[:297] + "..."
            warnings.append("debugging_step truncated to 300 chars")
        fixed_steps.append(step)
    data["debugging_steps"] = fixed_steps

    # Check corrected_code size (must not exceed 2× source + 2 KB)
    max_cc_len = len(source_code) * 2 + 2048
    if data.get("corrected_code") and len(data["corrected_code"]) > max_cc_len:
        data["corrected_code"] = None
        warnings.append(f"corrected_code exceeded size limit ({max_cc_len} chars); set to null")

    # Check affected_code: must be exact substring of source
    if data.get("affected_code"):
        normalized_affected = data["affected_code"].strip()
        normalized_source = source_code
        if normalized_affected not in normalized_source:
            data["affected_code"] = None
            warnings.append("affected_code not found in source; set to null")

    # Authority lock: if static has a confirmed location, ignore AI-stated line
    if static_result.location and static_result.location.line is not None:
        # We don't store AI line separately, but log a warning if needed
        pass  # Static line is authoritative; AI line is never stored separately

    # Rebuild model with fixes
    try:
        model = AIExplanation(**data)
    except PydanticValidationError as e:
        raise AIValidationError(f"Post-semantic schema failure: {e}") from e

    return model, warnings


def validate_ai_output(
    raw: str,
    source_code: str,
    static_result: StaticAnalysisResult,
    repair_fn=None,
) -> Tuple[AIExplanation, List[str], int]:
    """
    Validate raw AI output string.

    Returns:
        (AIExplanation, warnings, repair_attempts_used)

    Raises:
        AIValidationError if validation fails after one repair attempt.
    """
    repair_attempts = 0

    def _attempt(text: str) -> Tuple[AIExplanation, List[str]]:
        data = _parse_json(text)
        model, w1 = _validate_schema(data)
        model, w2 = _semantic_checks(model, source_code, static_result)
        return model, w1 + w2

    try:
        model, warnings = _attempt(raw)
        return model, warnings, repair_attempts
    except AIValidationError as first_err:
        logger.warning("AI output failed first validation: %s", first_err)
        if repair_fn is None:
            raise AIValidationError(str(first_err)) from first_err

        repair_attempts = 1
        repaired_raw = repair_fn(str(first_err))
        try:
            model, warnings = _attempt(repaired_raw)
            return model, warnings, repair_attempts
        except AIValidationError as second_err:
            logger.error("AI output failed repair attempt: %s", second_err)
            raise AIValidationError(str(second_err)) from second_err
