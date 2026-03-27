"""Google Gemini provider — native Gemini client via autogen-ext[gemini].

Setup: https://aistudio.google.com/app/apikey
Set GOOGLE_API_KEY in your .env file.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from autogen_ext.models.gemini import GeminiChatCompletionClient

RECOMMENDED_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]

DEFAULT_MODEL = "gemini-2.0-flash"

MODEL_INFO = {
    "vision": True,
    "function_calling": True,
    "json_output": True,
    "family": "gemini-2.0-flash",
    "structured_output": True,
}


def create_client(
    api_key: str,
    model: str | None = None,
    **kwargs,
) -> GeminiChatCompletionClient:
    """Create a Google Gemini chat completion client.

    Args:
        api_key: Google API key.
        model: Model name. Defaults to gemini-2.0-flash.
        **kwargs: Additional arguments passed to the client.

    Returns:
        Configured GeminiChatCompletionClient.
    """
    from autogen_ext.models.gemini import GeminiChatCompletionClient

    return GeminiChatCompletionClient(
        model=model or DEFAULT_MODEL,
        api_key=api_key,
        **kwargs,
    )
