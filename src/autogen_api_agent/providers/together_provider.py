"""Together.ai provider — OpenAI-compatible endpoint for open-source models.

Setup: https://api.together.xyz/settings/api-keys
Set TOGETHER_API_KEY in your .env file.
"""

from __future__ import annotations

from autogen_ext.models.openai import OpenAIChatCompletionClient

RECOMMENDED_MODELS = [
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    "mistralai/Mixtral-8x22B-Instruct-v0.1",
    "Qwen/Qwen2.5-72B-Instruct-Turbo",
    "deepseek-ai/DeepSeek-R1",
]

DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
BASE_URL = "https://api.together.xyz/v1"

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
    """Create a Together.ai chat completion client.

    Args:
        api_key: Together API key.
        model: Model name. Defaults to Llama-3.3-70B-Instruct-Turbo.
        base_url: Override the API base URL.
        **kwargs: Additional arguments passed to the client.

    Returns:
        Configured OpenAIChatCompletionClient for Together.ai.
    """
    return OpenAIChatCompletionClient(
        model=model or DEFAULT_MODEL,
        api_key=api_key,
        base_url=base_url or BASE_URL,
        model_info=MODEL_INFO,
        **kwargs,
    )
