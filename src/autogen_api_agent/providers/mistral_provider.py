"""Mistral provider — OpenAI-compatible endpoint.

Setup: https://console.mistral.ai/api-keys/
Set MISTRAL_API_KEY in your .env file.
"""

from __future__ import annotations

from autogen_ext.models.openai import OpenAIChatCompletionClient

RECOMMENDED_MODELS = [
    "mistral-large-latest",
    "mistral-medium-latest",
    "mistral-small-latest",
    "codestral-latest",
    "open-mistral-nemo",
]

DEFAULT_MODEL = "mistral-large-latest"
BASE_URL = "https://api.mistral.ai/v1"

MODEL_INFO = {
    "vision": False,
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
    """Create a Mistral chat completion client.

    Args:
        api_key: Mistral API key.
        model: Model name. Defaults to mistral-large-latest.
        base_url: Override the API base URL.
        **kwargs: Additional arguments passed to the client.

    Returns:
        Configured OpenAIChatCompletionClient for Mistral.
    """
    return OpenAIChatCompletionClient(
        model=model or DEFAULT_MODEL,
        api_key=api_key,
        base_url=base_url or BASE_URL,
        model_info=MODEL_INFO,
        **kwargs,
    )
