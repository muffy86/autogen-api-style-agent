from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from autogen_api_agent.models import ChatMessage
from autogen_api_agent.utils import extract_final_response, extract_message_text, format_task


def _make_result(*contents) -> MagicMock:
    result = MagicMock()
    result.messages = [MagicMock(content=content) for content in contents]
    return result


def test_extract_final_response_extracts_last_assistant_message_text() -> None:
    result = _make_result("first", "final answer")

    assert extract_final_response(result) == "final answer"


def test_extract_final_response_skips_terminate_messages() -> None:
    result = _make_result("useful answer", "TERMINATE")

    assert extract_final_response(result) == "useful answer"


def test_extract_final_response_handles_multimodal_list_content() -> None:
    text_part = MagicMock()
    text_part.text = "world"
    result = _make_result(["hello", text_part])

    assert extract_final_response(result) == "hello world"


def test_extract_final_response_returns_default_for_empty_results() -> None:
    result = MagicMock(messages=[])

    assert extract_final_response(result) == "No response generated."


def test_extract_message_text_extracts_text_from_streaming_message() -> None:
    message = SimpleNamespace(content="stream chunk")

    assert extract_message_text(message) == "stream chunk"


def test_extract_message_text_returns_empty_string_for_task_result_wrappers() -> None:
    wrapper = MagicMock(messages=[MagicMock(content="ignored")])

    assert extract_message_text(wrapper) == ""


def test_extract_message_text_returns_empty_string_for_terminate() -> None:
    message = MagicMock(content="TERMINATE")

    assert extract_message_text(message) == ""


def test_format_task_formats_single_message() -> None:
    messages = [ChatMessage(role="user", content="hello")]

    assert format_task(messages) == "hello"


def test_format_task_formats_multi_message_conversation_with_role_prefixes() -> None:
    messages = [
        ChatMessage(role="system", content="be concise"),
        ChatMessage(role="user", content="question"),
        ChatMessage(role="assistant", content="answer"),
    ]

    assert format_task(messages) == (
        "[system]: be concise\n\n[user]: question\n\n[assistant]: answer"
    )


def test_format_task_returns_empty_string_for_empty_list() -> None:
    assert format_task([]) == ""
