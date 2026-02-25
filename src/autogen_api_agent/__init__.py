"""autogen-api-style-agent — Maxed-out multi-agent productivity system."""

__version__ = "0.1.0"

from .config import AppConfig, ProviderConfig, get_config
from .models import (
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
)
from .providers.factory import ModelClientFactory
from .session import Session, SessionManager

__all__ = [
    "__version__",
    "AppConfig",
    "ProviderConfig",
    "get_config",
    "ModelClientFactory",
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "ChatCompletionChunk",
    "ChatMessage",
    "Session",
    "SessionManager",
]
