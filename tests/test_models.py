from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from autogen_api_agent.models import (
    ChatChoice,
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    StreamChoice,
    StreamDelta,
    Usage,
)


@pytest.mark.parametrize("role", ["system", "user", "assistant"])
def test_chat_message_creation_with_valid_roles(role: str) -> None:
    message = ChatMessage(role=role, content="hello")

    assert message.role == role
    assert message.content == "hello"


def test_chat_completion_request_defaults() -> None:
    request = ChatCompletionRequest(messages=[ChatMessage(role="user", content="hi")])

    assert request.model == "auto"
    assert request.team == "productivity"
    assert request.stream is False
    assert request.temperature is None
    assert request.max_tokens is None
    assert request.session_id is None


def test_chat_completion_request_with_all_fields_populated() -> None:
    request = ChatCompletionRequest(
        messages=[
            ChatMessage(role="system", content="be helpful"),
            ChatMessage(role="user", content="solve this"),
        ],
        model="openai/gpt-4o",
        team="quick",
        stream=True,
        temperature=0.2,
        max_tokens=512,
        session_id="session-123",
    )

    assert request.model == "openai/gpt-4o"
    assert request.team == "quick"
    assert request.stream is True
    assert request.temperature == 0.2
    assert request.max_tokens == 512
    assert request.session_id == "session-123"
    assert [message.role for message in request.messages] == ["system", "user"]


def test_chat_completion_response_auto_generates_id_and_created_timestamp() -> None:
    fake_uuid = MagicMock(hex="abcdef1234567890")

    with (
        patch("autogen_api_agent.models.uuid.uuid4", return_value=fake_uuid),
        patch("autogen_api_agent.models.time.time", return_value=1_700_000_000),
    ):
        response = ChatCompletionResponse(
            model="openai/gpt-4o",
            choices=[ChatChoice(message=ChatMessage(role="assistant", content="done"))],
        )

    assert response.id == "chatcmpl-abcdef12"
    assert response.created == 1_700_000_000
    assert response.usage == Usage()


def test_chat_completion_chunk_for_streaming() -> None:
    chunk = ChatCompletionChunk(
        id="chatcmpl-test",
        created=1_700_000_000,
        model="auto",
        choices=[StreamChoice(delta=StreamDelta(role="assistant", content="hello"))],
    )

    assert chunk.object == "chat.completion.chunk"
    assert chunk.choices[0].delta.role == "assistant"
    assert chunk.choices[0].delta.content == "hello"


def test_stream_delta_supports_role_only_content_only_and_both() -> None:
    role_only = StreamDelta(role="assistant")
    content_only = StreamDelta(content="partial")
    both = StreamDelta(role="assistant", content="partial")

    assert role_only.role == "assistant"
    assert role_only.content is None
    assert content_only.role is None
    assert content_only.content == "partial"
    assert both.role == "assistant"
    assert both.content == "partial"


def test_usage_defaults_to_zero_counts() -> None:
    usage = Usage()

    assert usage.prompt_tokens == 0
    assert usage.completion_tokens == 0
    assert usage.total_tokens == 0


def test_chat_message_rejects_invalid_roles() -> None:
    with pytest.raises(ValidationError):
        ChatMessage(role="tool", content="nope")
