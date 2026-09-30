"""
AI provider abstraction (§7.1).

AIProvider protocol: generate_structured(system_prompt, payload, json_schema) -> raw_text
"""
from typing import Protocol, Any, Dict


class AIProvider(Protocol):
    """Provider interface — never raises; callers handle exceptions."""

    def generate_structured(
        self,
        system_prompt: str,
        payload: Dict[str, Any],
        json_schema: Dict[str, Any],
    ) -> str:
        """Call the underlying model; return raw text. Never raises."""
        ...
