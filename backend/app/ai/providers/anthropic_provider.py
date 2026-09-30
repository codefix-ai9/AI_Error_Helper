"""
AnthropicProvider — calls Claude via the anthropic SDK (§7.1).

Selected when LLM_PROVIDER=anthropic.
Keys, model, and timeouts come from settings only.
"""
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AnthropicProvider:
    def __init__(self, api_key: str, model: str, timeout_s: int = 20):
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_s

    def generate_structured(
        self,
        system_prompt: str,
        payload: Dict[str, Any],
        json_schema: Dict[str, Any],
    ) -> str:
        try:
            import anthropic  # type: ignore
        except ImportError:
            logger.error("anthropic SDK not installed; run: pip install anthropic")
            raise RuntimeError("anthropic SDK not installed")

        client = anthropic.Anthropic(api_key=self._api_key)
        user_msg = (
            "Analyze the following programming error and return ONLY JSON.\n\n"
            + json.dumps(payload, ensure_ascii=False)
        )
        message = client.messages.create(
            model=self._model,
            max_tokens=1024,
            temperature=0.1,
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
            timeout=self._timeout,
        )
        return message.content[0].text
