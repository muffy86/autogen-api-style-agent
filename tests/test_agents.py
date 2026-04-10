from __future__ import annotations

from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
from autogen_agentchat.agents import AssistantAgent

from autogen_api_agent.agents import (
    create_architect,
    create_coder,
    create_devops,
    create_orchestrator,
    create_researcher,
    create_reviewer,
    create_tester,
    create_writer,
)
from autogen_api_agent.agents.base import create_agent, get_tools


def _tool_names(agent: AssistantAgent) -> set[str]:
    return {tool.name for tool in agent._tools}


@pytest.mark.parametrize(
    ("factory", "expected_name"),
    [
        (create_coder, "coder"),
        (create_reviewer, "reviewer"),
        (create_researcher, "researcher"),
        (create_architect, "architect"),
        (create_tester, "tester"),
        (create_writer, "writer"),
        (create_devops, "devops"),
        (create_orchestrator, "orchestrator"),
    ],
)
def test_create_agent_functions_return_assistant_agents_with_correct_names(
    factory: Callable,
    expected_name: str,
) -> None:
    agent = factory(MagicMock())

    assert isinstance(agent, AssistantAgent)
    assert agent.name == expected_name


def test_create_coder_has_file_ops_shell_and_code_analysis_tools() -> None:
    agent = create_coder(MagicMock())

    assert _tool_names(agent) == {
        "read_file",
        "write_file",
        "list_directory",
        "search_files",
        "find_in_files",
        "run_command",
        "analyze_python_file",
        "check_syntax",
    }


def test_create_reviewer_has_file_ops_and_code_analysis_tools() -> None:
    agent = create_reviewer(MagicMock())

    assert _tool_names(agent) == {
        "read_file",
        "write_file",
        "list_directory",
        "search_files",
        "find_in_files",
        "analyze_python_file",
        "check_syntax",
    }


def test_create_researcher_has_web_search_and_github_tools() -> None:
    agent = create_researcher(MagicMock())

    assert _tool_names(agent) == {
        "web_search",
        "fetch_url",
        "get_repo_info",
        "list_issues",
        "create_issue",
        "get_pr_diff",
    }


def test_create_architect_has_file_ops_and_code_analysis_tools() -> None:
    agent = create_architect(MagicMock())

    assert _tool_names(agent) == {
        "read_file",
        "write_file",
        "list_directory",
        "search_files",
        "find_in_files",
        "analyze_python_file",
        "check_syntax",
    }


def test_create_tester_has_file_ops_shell_and_code_analysis_tools() -> None:
    agent = create_tester(MagicMock())

    assert _tool_names(agent) == {
        "read_file",
        "write_file",
        "list_directory",
        "search_files",
        "find_in_files",
        "run_command",
        "analyze_python_file",
        "check_syntax",
    }


def test_create_writer_has_file_ops_and_web_search_tools() -> None:
    agent = create_writer(MagicMock())

    assert _tool_names(agent) == {
        "read_file",
        "write_file",
        "list_directory",
        "search_files",
        "find_in_files",
        "web_search",
        "fetch_url",
    }


def test_create_devops_has_file_ops_and_shell_tools() -> None:
    agent = create_devops(MagicMock())

    assert _tool_names(agent) == {
        "read_file",
        "write_file",
        "list_directory",
        "search_files",
        "find_in_files",
        "run_command",
    }


def test_create_orchestrator_has_no_tools_by_default() -> None:
    agent = create_orchestrator(MagicMock())

    assert agent._tools == []


def test_get_tools_returns_correct_tools_for_each_set() -> None:
    assert {tool.__name__ for tool in get_tools("file_ops")} == {
        "read_file",
        "write_file",
        "list_directory",
        "search_files",
        "find_in_files",
    }
    assert {tool.__name__ for tool in get_tools("web_search")} == {"web_search", "fetch_url"}
    assert {tool.__name__ for tool in get_tools("github")} == {
        "get_repo_info",
        "list_issues",
        "create_issue",
        "get_pr_diff",
    }
    assert {tool.__name__ for tool in get_tools("shell")} == {"run_command"}
    assert {tool.__name__ for tool in get_tools("code_analysis")} == {
        "analyze_python_file",
        "check_syntax",
    }


def test_get_tools_returns_empty_list_for_unknown_tool_set() -> None:
    assert get_tools("does_not_exist") == []


def test_create_agent_helper_works_with_tool_sets() -> None:
    agent = create_agent(
        name="helper",
        system_message="help",
        model_client=MagicMock(),
        tool_sets=["file_ops", "shell"],
    )

    assert isinstance(agent, AssistantAgent)
    assert agent.name == "helper"
    assert _tool_names(agent) == {
        "read_file",
        "write_file",
        "list_directory",
        "search_files",
        "find_in_files",
        "run_command",
    }
