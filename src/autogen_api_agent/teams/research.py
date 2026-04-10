from __future__ import annotations

from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat

from ..agents.architect import create_architect
from ..agents.researcher import create_researcher
from ..agents.writer import create_writer
from ..config import AppConfig, get_config
from ..providers.factory import ModelClientFactory


def create_research_team(
    factory: ModelClientFactory,
    provider: str | None = None,
    model: str | None = None,
    config: AppConfig | None = None,
):
    """Create a 3-agent research + summary team.

    Flow: researcher -> writer -> architect (round-robin).
    The researcher gathers information, the writer drafts a report,
    and the architect provides structural feedback.
    """
    config = config or get_config()
    client = factory.create(provider, model)

    researcher = create_researcher(client)
    writer = create_writer(client)
    architect = create_architect(client)

    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(config.max_turns)

    team = RoundRobinGroupChat(
        participants=[researcher, writer, architect],
        termination_condition=termination,
    )
    return team
