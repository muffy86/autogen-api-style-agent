"""Kimi K2.5 / Moonshot provider — OpenAI-compatible endpoint.

Setup: https://platform.moonshot.cn/console/api-keys
Set MOONSHOT_API_KEY in your .env file.
"""

from __future__ import annotations

from autogen_ext.models.openai import OpenAIChatCompletionClient

RECOMMENDED_MODELS = [
    "kimi-k2.5",
    "moonshot-v1-128k",
    "moonshot-v1-32k",
    "moonshot-v1-8k",
]

DEFAULT_MODEL = "kimi-k2.5"
BASE_URL = "https://api.moonshot.cn/v1"

MODEL_INFO = {
    "vision": True,
    "function_calling": True,
    "json_output": True,
    "family": "unknown",
    "structured_output": True,
}


def create_client(
    api_key: str,
    model: str | None = None,
    base_url: str | None = None,
    **kwargs,
) -> OpenAIChatCompletionClient:
    """Create a Kimi/Moonshot chat completion client.

    Args:
        api_key: Moonshot API key.
        model: Model name. Defaults to kimi-k2.5.
        base_url: Override the API base URL.
        **kwargs: Additional arguments passed to the client.

    Returns:
        Configured OpenAIChatCompletionClient for Kimi/Moonshot.
    """
    return OpenAIChatCompletionClient(
        model=model or DEFAULT_MODEL,
        api_key=api_key,
        base_url=base_url or BASE_URL,
        model_info=MODEL_INFO,
        **kwargs,
    )
