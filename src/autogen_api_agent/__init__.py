"""autogen-api-style-agent — Maxed-out multi-agent productivity system."""

__version__ = "0.1.0"

from .cli import app as cli_app
from .config import AppConfig, ProviderConfig, get_config
from .mcp_server import create_mcp_server, run_mcp_stdio
from .models import (
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
)
from .providers.factory import ModelClientFactory
from .server import app, create_app
from .session import Session, SessionManager
from .utils import extract_final_response, extract_message_text

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
    "app",
    "create_app",
    "cli_app",
    "create_mcp_server",
    "run_mcp_stdio",
    "extract_final_response",
    "extract_message_text",
]
