from __future__ import annotations

from collections.abc import Callable

from autogen_agentchat.agents import AssistantAgent

from ..tools.code_analysis import analyze_python_file, check_syntax
from ..tools.file_ops import (
    find_in_files,
    list_directory,
    read_file,
    search_files,
    write_file,
)
from ..tools.github_tools import create_issue, get_pr_diff, get_repo_info, list_issues
from ..tools.shell_exec import run_command
from ..tools.web_search import fetch_url, web_search

TOOL_SETS: dict[str, list[Callable]] = {
    "file_ops": [read_file, write_file, list_directory, search_files, find_in_files],
    "web_search": [web_search, fetch_url],
    "github": [get_repo_info, list_issues, create_issue, get_pr_diff],
    "shell": [run_command],
    "code_analysis": [analyze_python_file, check_syntax],
}


def get_tools(*tool_set_names: str) -> list[Callable]:
    """Get a combined list of tool functions by set name."""
    tools: list[Callable] = []
    for name in tool_set_names:
        if name in TOOL_SETS:
            tools.extend(TOOL_SETS[name])
    return tools


def create_agent(
    name: str,
    system_message: str,
    model_client,
    tool_sets: list[str] | None = None,
    description: str = "",
    extra_tools: list[Callable] | None = None,
) -> AssistantAgent:
    """Helper to create a configured AssistantAgent with tool sets."""
    tools = get_tools(*(tool_sets or []))
    if extra_tools:
        tools.extend(extra_tools)

    return AssistantAgent(
        name=name,
        model_client=model_client,
        tools=tools,
        system_message=system_message,
        description=description,
    )
