"""Shared utilities for extracting responses from AutoGen message types."""
from __future__ import annotations

from typing import Any


def extract_final_response(result: Any) -> str:
    """Extract the final text response from a TaskResult.

    Handles TextMessage, MultiModalMessage, ToolCallRequestEvent,
    ToolCallExecutionEvent, and other AutoGen message types.
    Walks ``result.messages`` in reverse to find the last meaningful
    assistant message, skipping TERMINATE markers.
    """
    messages = getattr(result, "messages", None)
    if not messages:
        return "No response generated."

    for msg in reversed(messages):
        content = getattr(msg, "content", None)
        if isinstance(content, str):
            text = content.strip()
            if text and text != "TERMINATE":
                return text
        elif isinstance(content, list):
            parts: list[str] = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                elif hasattr(part, "text"):
                    parts.append(part.text)
            combined = " ".join(parts).strip()
            if combined and combined != "TERMINATE":
                return combined
    return "No response generated."


def extract_message_text(message: Any) -> str:
    """Extract displayable text from a single streaming message.

    Returns an empty string for non-text messages (TaskResult wrappers,
    ToolCallRequestEvent, ToolCallExecutionEvent, etc.) so callers can
    safely skip them.
    """
    if hasattr(message, "messages"):
        return ""

    content = getattr(message, "content", None)
    if isinstance(content, str):
        text = content.strip()
        if text and text != "TERMINATE":
            return text
    elif isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif hasattr(part, "text"):
                parts.append(part.text)
        combined = " ".join(parts).strip()
        if combined and combined != "TERMINATE":
            return combined
    return ""
