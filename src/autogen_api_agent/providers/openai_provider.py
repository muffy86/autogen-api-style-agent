"""OpenAI provider — GPT-4o, GPT-4-turbo, o1, o3 series.

Setup: https://platform.openai.com/api-keys
Set OPENAI_API_KEY in your .env file.
"""

from __future__ import annotations

from autogen_ext.models.openai import OpenAIChatCompletionClient

RECOMMENDED_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "o1",
    "o3-mini",
]

DEFAULT_MODEL = "gpt-4o"

MODEL_INFO = {
    "vision": True,
    "function_calling": True,
    "json_output": True,
    "family": "gpt-4o",
    "structured_output": True,
}


def create_client(
    api_key: str,
    model: str | None = None,
    **kwargs,
) -> OpenAIChatCompletionClient:
    """Create an OpenAI chat completion client.

    Args:
        api_key: OpenAI API key.
        model: Model name. Defaults to gpt-4o.
        **kwargs: Additional arguments passed to the client.

    Returns:
        Configured OpenAIChatCompletionClient.
    """
    return OpenAIChatCompletionClient(
        model=model or DEFAULT_MODEL,
        api_key=api_key,
        **kwargs,
    )
