"""
OpenAICompatibleProvider — works with OpenAI and any OpenAI-compatible endpoint (§7.1).

Selected when LLM_PROVIDER=openai.
Keys, model, and timeouts come from settings only.
"""
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider:
    def __init__(self, api_key: str, model: str, timeout_s: int = 20, base_url: str = None):
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_s
        self._base_url = base_url

    def generate_structured(
        self,
        system_prompt: str,
        payload: Dict[str, Any],
        json_schema: Dict[str, Any],
    ) -> str:
        try:
            import openai  # type: ignore
        except ImportError:
            logger.error("openai SDK not installed; run: pip install openai")
            raise RuntimeError("openai SDK not installed")

        kwargs = dict(api_key=self._api_key)
        if self._base_url:
            kwargs["base_url"] = self._base_url
        client = openai.OpenAI(**kwargs)
        user_msg = (
            "Analyze the following programming error and return ONLY JSON.\n\n"
            + json.dumps(payload, ensure_ascii=False)
        )
        response = client.chat.completions.create(
            model=self._model,
            temperature=0.1,
            max_tokens=1024,
            timeout=self._timeout,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
