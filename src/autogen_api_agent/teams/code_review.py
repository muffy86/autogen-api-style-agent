from __future__ import annotations

from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat

from ..agents.architect import create_architect
from ..agents.coder import create_coder
from ..agents.reviewer import create_reviewer
from ..config import AppConfig, get_config
from ..providers.factory import ModelClientFactory


def create_code_review_team(
    factory: ModelClientFactory,
    provider: str | None = None,
    model: str | None = None,
    config: AppConfig | None = None,
):
    """Create a focused 3-agent code review team.

    Flow: coder -> reviewer -> architect (round-robin).
    The coder presents code, the reviewer finds issues, and the architect
    evaluates structural/design concerns.
    """
    config = config or get_config()
    client = factory.create(provider, model)

    coder = create_coder(client)
    reviewer = create_reviewer(client)
    architect = create_architect(client)

    termination = (
        TextMentionTermination("TERMINATE")
        | MaxMessageTermination(config.max_turns)
    )

    team = RoundRobinGroupChat(
        participants=[coder, reviewer, architect],
        termination_condition=termination,
    )
    return team
