"""
AI Engine (§7.1–7.5, 7.8).

build_ai_engine(settings) -> AIEnginePort  (the sole public factory)

Pipeline per call:
  1. Build structured payload from AIRequestContext.
  2. Apply prompt-injection–safe delimiters.
  3. Call provider with timeout + 1 retry on 429/5xx.
  4. Validate response (via ai.validator).
  5. Convert to AIOutcome (suggestions list + metadata).
  6. On any failure → AIOutcome(status=...) — NEVER raises.
"""
import json
import logging
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

from backend.app.application.ports import AIEnginePort
from backend.app.models.stages import AIRequestContext, AIOutcome, AISuggestion
from backend.app.models.enums import AIStatus, ErrorType
from backend.app.core.config import Settings
from backend.app.ai.schemas import AIExplanation
from backend.app.ai.validator import validate_ai_output, AIValidationError

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent / "prompts"
PROMPT_VERSION = "v1"

# JSON schema hint passed to providers that support it
_AI_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "explanation": {"type": "string"},
        "probable_cause": {"type": "string"},
        "affected_code": {"type": ["string", "null"]},
        "corrected_code": {"type": ["string", "null"]},
        "debugging_steps": {"type": "array", "items": {"type": "string"}},
        "prevention_tip": {"type": "string"},
        "key_concept": {"type": "string"},
        "uncertainty_note": {"type": "string"},
        "suggested_category": {"type": ["string", "null"]},
    },
    "required": [
        "explanation", "probable_cause", "debugging_steps",
        "prevention_tip", "key_concept", "uncertainty_note",
    ],
}


def _load_system_prompt() -> str:
    path = _PROMPT_DIR / f"system_{PROMPT_VERSION}.txt"
    return path.read_text(encoding="utf-8")


def _build_payload(ctx: AIRequestContext) -> Dict[str, Any]:
    """Build a structured, injection-safe payload."""
    ni = ctx.normalized_input
    sr = ctx.static_result

    # Wrap untrusted user data in delimiters (§7.2 injection defense)
    source_delimited = (
        "<source_code>\n"
        + ni.source_code
        + "\n</source_code>"
    )
    error_delimited = (
        "<error_output>\n"
        + ni.error_text_clean
        + "\n</error_output>"
    )

    findings_list = [
        {
            "rule_id": f.rule_id,
            "category": f.category,
            "evidence_level": f.evidence_level.value,
            "message": f.message,
            "location": {
                "line": f.location.line,
                "column": f.location.column,
            } if f.location else None,
            "snippet": f.snippet,
        }
        for f in sr.findings
    ]

    return {
        "language": ni.language.value,
        "source_code": source_delimited,
        "error_input": error_delimited,
        "static_findings": findings_list,
        "detected_category": sr.error_type.value,
        "severity": sr.severity.value,
        "evidence_level": sr.evidence_level.value,
        "location": {
            "line": sr.location.line,
            "column": sr.location.column,
        } if sr.location else None,
        "expected_behavior": ni.expected_behavior,
    }


def _suggestions_from_explanation(exp: AIExplanation, error_type: ErrorType) -> list:
    """Convert AIExplanation to AISuggestion list."""
    suggestions = []
    if exp.explanation:
        suggestions.append(AISuggestion(kind="explanation", text=exp.explanation, provenance="ai"))
    if exp.probable_cause:
        suggestions.append(AISuggestion(kind="explanation", text=f"Probable cause: {exp.probable_cause}", provenance="ai"))
    if exp.corrected_code:
        suggestions.append(AISuggestion(kind="correction", text=exp.corrected_code, provenance="ai"))
    for step in (exp.debugging_steps or []):
        suggestions.append(AISuggestion(kind="debug_step", text=step, provenance="ai"))
    if exp.prevention_tip:
        suggestions.append(AISuggestion(kind="prevention", text=exp.prevention_tip, provenance="ai"))
    if exp.suggested_category and error_type == ErrorType.UNKNOWN:
        suggestions.append(AISuggestion(kind="suggested_category", text=exp.suggested_category, provenance="ai"))
    return suggestions


class RealAIEngine(AIEnginePort):
    def __init__(self, provider, settings: Settings):
        self._provider = provider
        self._settings = settings
        self._system_prompt = _load_system_prompt()

    def explain(self, ctx: AIRequestContext) -> AIOutcome:
        t_start = time.monotonic()
        repair_attempts = 0
        warnings: list = []

        try:
            payload = _build_payload(ctx)
            source_code = ctx.normalized_input.source_code

            # Log size + hash, never contents (§7.8)
            if not self._settings.LOG_AI_PAYLOADS:
                h = hashlib.sha256(source_code.encode()).hexdigest()[:8]
                logger.info(
                    "AI call: lang=%s source_len=%d error_len=%d hash=%s",
                    ctx.normalized_input.language.value,
                    len(source_code),
                    len(ctx.normalized_input.error_text_clean),
                    h,
                )

            raw = self._call_with_retry(payload)
            latency_ms = int((time.monotonic() - t_start) * 1000)

            # Repair function — sends validation errors back to provider
            def repair_fn(error_msg: str) -> str:
                repair_payload = dict(payload)
                repair_payload["validation_errors"] = error_msg
                repair_payload["instruction"] = (
                    "The previous response failed validation. "
                    "Fix the listed errors and return only valid JSON."
                )
                return self._call_with_retry(repair_payload)

            explanation, val_warnings, repair_attempts = validate_ai_output(
                raw, source_code, ctx.static_result, repair_fn=repair_fn
            )
            warnings.extend(val_warnings)

            suggestions = _suggestions_from_explanation(explanation, ctx.static_result.error_type)

            provider_name = type(self._provider).__name__
            model_name = getattr(self._settings, "LLM_MODEL", "")

            return AIOutcome(
                status=AIStatus.OK,
                payload=explanation.model_dump(),
                provider=provider_name,
                model=model_name,
                latency_ms=latency_ms,
                repair_attempts=repair_attempts,
                warnings=warnings,
                suggestions=suggestions,
            )

        except AIValidationError as e:
            latency_ms = int((time.monotonic() - t_start) * 1000)
            logger.warning("AI validation error after %d repair attempt(s): %s", repair_attempts, e)
            return AIOutcome(
                status=AIStatus.INVALID_RESPONSE,
                latency_ms=latency_ms,
                repair_attempts=repair_attempts,
                warnings=[str(e)],
            )
        except TimeoutError as e:
            latency_ms = int((time.monotonic() - t_start) * 1000)
            logger.warning("AI timeout: %s", e)
            return AIOutcome(status=AIStatus.TIMEOUT, latency_ms=latency_ms, repair_attempts=repair_attempts)
        except Exception as e:
            latency_ms = int((time.monotonic() - t_start) * 1000)
            logger.error("AI provider error: %s: %s", type(e).__name__, e)
            return AIOutcome(status=AIStatus.UNAVAILABLE, latency_ms=latency_ms, repair_attempts=repair_attempts, warnings=[str(e)])

    def _call_with_retry(self, payload: Dict[str, Any]) -> str:
        """Call provider; retry once on timeout/5xx/429."""
        import socket

        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                return self._provider.generate_structured(
                    self._system_prompt, payload, _AI_JSON_SCHEMA
                )
            except Exception as e:
                err_str = str(e).lower()
                is_retryable = (
                    "429" in err_str
                    or "503" in err_str
                    or "502" in err_str
                    or "500" in err_str
                    or "timeout" in err_str
                    or isinstance(e, (TimeoutError, socket.timeout, ConnectionError))
                )
                if is_retryable and attempt < max_attempts - 1:
                    logger.warning("AI call failed (%s), retrying after backoff...", e)
                    time.sleep(1.5)
                    continue
                raise


class NullAIEngine(AIEnginePort):
    """Used when LLM_PROVIDER=disabled."""
    def explain(self, ctx: AIRequestContext) -> AIOutcome:
        return AIOutcome(status=AIStatus.DISABLED)


class MockAIEngine(AIEnginePort):
    """Wraps the MockProvider through the full validation pipeline."""
    def __init__(self, settings: Settings):
        from backend.app.ai.providers.mock_provider import MockProvider
        self._inner = RealAIEngine(MockProvider(), settings)

    def explain(self, ctx: AIRequestContext) -> AIOutcome:
        outcome = self._inner.explain(ctx)
        # Override status to MOCK regardless of what RealAIEngine returned
        if outcome.status == AIStatus.OK:
            outcome = AIOutcome(
                status=AIStatus.MOCK,
                payload=outcome.payload,
                provider="MockProvider",
                model="mock",
                latency_ms=outcome.latency_ms,
                repair_attempts=outcome.repair_attempts,
                warnings=outcome.warnings,
                suggestions=outcome.suggestions,
            )
        return outcome


def build_ai_engine(settings: Settings) -> AIEnginePort:
    """
    Factory function (§7.1).
    Selected by LLM_PROVIDER env var.
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "disabled":
        return NullAIEngine()

    if provider == "mock" or not settings.LLM_API_KEY:
        return MockAIEngine(settings)

    if provider == "anthropic":
        from backend.app.ai.providers.anthropic_provider import AnthropicProvider
        p = AnthropicProvider(
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
            timeout_s=settings.AI_TIMEOUT_S,
        )
        return RealAIEngine(p, settings)

    if provider == "openai":
        from backend.app.ai.providers.openai_provider import OpenAICompatibleProvider
        p = OpenAICompatibleProvider(
            api_key=settings.LLM_API_KEY,
            model=settings.LLM_MODEL,
            timeout_s=settings.AI_TIMEOUT_S,
        )
        return RealAIEngine(p, settings)

    logger.warning("Unknown LLM_PROVIDER '%s', falling back to mock", provider)
    return MockAIEngine(settings)
