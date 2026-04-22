"""autogen-api-style-agent — Maxed-out multi-agent productivity system."""

__version__ = "0.2.0"

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
from .utils import extract_final_response, extract_message_text, format_task
from .openapi_spec import OPENAPI_SPEC

try:
    from .providers.swiss_public_ai import SwissAIClient, list_all_providers
except (ImportError, FileNotFoundError):
    SwissAIClient = None
    list_all_providers = None

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
    "OPENAPI_SPEC",
    "cli_app",
    "create_mcp_server",
    "run_mcp_stdio",
    "extract_final_response",
    "extract_message_text",
    "format_task",
    "SwissAIClient",
    "list_all_providers",
]
