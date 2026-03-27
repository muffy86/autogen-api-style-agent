"""OpenRouter provider — unified gateway to 200+ models via OpenAI-compatible API.

Setup: https://openrouter.ai/keys
Set OPENROUTER_API_KEY in your .env file.
"""

from __future__ import annotations

from autogen_ext.models.openai import OpenAIChatCompletionClient

RECOMMENDED_MODELS = [
    "openai/gpt-4o",
    "anthropic/claude-3.5-sonnet",
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.3-70b-instruct",
    "deepseek/deepseek-r1",
]

DEFAULT_MODEL = "openai/gpt-4o"
BASE_URL = "https://openrouter.ai/api/v1"

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
    """Create an OpenRouter chat completion client.

    Args:
        api_key: OpenRouter API key.
        model: Model name. Defaults to openai/gpt-4o.
        base_url: Override the API base URL.
        **kwargs: Additional arguments passed to the client.

    Returns:
        Configured OpenAIChatCompletionClient for OpenRouter.
    """
    return OpenAIChatCompletionClient(
        model=model or DEFAULT_MODEL,
        api_key=api_key,
        base_url=base_url or BASE_URL,
        model_info=MODEL_INFO,
        **kwargs,
    )
