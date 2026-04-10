from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat

from autogen_api_agent.config import AppConfig
from autogen_api_agent.teams import _TEAM_MAP, create_team


def _make_factory() -> MagicMock:
    factory = MagicMock()
    factory.create.return_value = MagicMock()
    return factory


def _participant_names(team) -> list[str]:
    return [participant.name for participant in team._participants]


def _tool_names(agent: AssistantAgent) -> set[str]:
    return {tool.name for tool in agent._tools}


def test_create_team_productivity_returns_selector_group_chat_with_eight_participants() -> None:
    team = create_team(
        "productivity",
        factory=_make_factory(),
        config=AppConfig(_env_file=None, max_turns=5),
    )

    assert isinstance(team, SelectorGroupChat)
    assert len(team._participants) == 8
    assert _participant_names(team) == [
        "orchestrator",
        "coder",
        "reviewer",
        "researcher",
        "architect",
        "tester",
        "writer",
        "devops",
    ]


def test_create_team_code_review_returns_round_robin_group_chat_with_three_participants() -> None:
    team = create_team(
        "code_review",
        factory=_make_factory(),
        config=AppConfig(_env_file=None, max_turns=5),
    )

    assert isinstance(team, RoundRobinGroupChat)
    assert len(team._participants) == 3
    assert _participant_names(team) == ["coder", "reviewer", "architect"]


def test_create_team_research_returns_round_robin_group_chat_with_three_participants() -> None:
    team = create_team(
        "research",
        factory=_make_factory(),
        config=AppConfig(_env_file=None, max_turns=5),
    )

    assert isinstance(team, RoundRobinGroupChat)
    assert len(team._participants) == 3
    assert _participant_names(team) == ["researcher", "writer", "architect"]


def test_create_team_quick_returns_assistant_agent_with_all_tools() -> None:
    team = create_team(
        "quick",
        factory=_make_factory(),
        config=AppConfig(_env_file=None, max_turns=5),
    )

    assert isinstance(team, AssistantAgent)
    assert team.name == "assistant"
    assert _tool_names(team) == {
        "read_file",
        "write_file",
        "list_directory",
        "search_files",
        "find_in_files",
        "web_search",
        "fetch_url",
        "get_repo_info",
        "list_issues",
        "create_issue",
        "get_pr_diff",
        "run_command",
        "analyze_python_file",
        "check_syntax",
    }


def test_create_team_invalid_name_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Unknown team"):
        create_team("invalid")


def test_team_registry_has_exactly_four_entries() -> None:
    assert len(_TEAM_MAP) == 4
    assert set(_TEAM_MAP) == {"productivity", "code_review", "research", "quick"}
