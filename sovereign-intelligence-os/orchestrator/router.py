from __future__ import annotations

import logging
from typing import Any

import litellm

log = logging.getLogger(__name__)


class LLMRouter:
    def __init__(self, default_model: str, timeout: float = 60.0) -> None:
        self.default_model = default_model
        self.timeout = timeout

    async def complete(
        self,
        user_message: str,
        system_prompt: str = "",
        model: str | None = None,
        extra_messages: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if extra_messages:
            messages.extend(extra_messages)
        messages.append({"role": "user", "content": user_message})
        try:
            response = await litellm.acompletion(
                model=model or self.default_model,
                messages=messages,
                timeout=self.timeout,
            )
            content = response["choices"][0]["message"]["content"]
            return {"ok": True, "model": response.get("model"), "content": content}
        except Exception as exc:
            log.exception("LLM completion failed")
            return {"ok": False, "error": str(exc), "content": ""}
