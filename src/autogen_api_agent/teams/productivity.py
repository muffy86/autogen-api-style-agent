from __future__ import annotations

from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat

from ..agents.architect import create_architect
from ..agents.coder import create_coder
from ..agents.devops import create_devops
from ..agents.orchestrator import create_orchestrator
from ..agents.researcher import create_researcher
from ..agents.reviewer import create_reviewer
from ..agents.tester import create_tester
from ..agents.writer import create_writer
from ..config import AppConfig, get_config
from ..providers.factory import ModelClientFactory

SELECTOR_PROMPT = """\
You are the team coordinator. Based on the conversation so far, select the next agent to speak.

Available agents and their specialties:
- orchestrator: Plans tasks, delegates work, synthesizes results.
  Pick when planning is needed or when combining work from multiple agents.
- coder: Writes and edits code.
  Pick when code needs to be written, modified, debugged, or refactored.
- reviewer: Reviews code quality.
  Pick when code needs quality review, security audit, or style check.
- researcher: Finds information online.
  Pick when questions need web research, docs lookup, or GitHub analysis.
- architect: Designs systems and APIs.
  Pick for system design, API design, database schema, or architecture.
- tester: Writes and runs tests.
  Pick when code needs test coverage or existing tests need to be run.
- writer: Writes documentation.
  Pick when READMEs, docs, tutorials, or technical writing is needed.
- devops: Handles CI/CD and deployment.
  Pick when Dockerfiles, pipelines, infra configs, or deploy scripts are needed.

Rules:
- Start with orchestrator for complex multi-step tasks.
- For simple single-domain tasks, go directly to the specialist.
- After an agent completes their work, route back to orchestrator for synthesis.
- Never pick the same agent twice in a row unless they explicitly need to continue.

Read the conversation and select the most appropriate next agent.\
"""


def create_productivity_team(
    factory: ModelClientFactory,
    provider: str | None = None,
    model: str | None = None,
    config: AppConfig | None = None,
):
    """Create the full 8-agent productivity team using SelectorGroupChat."""
    config = config or get_config()
    client = factory.create(provider, model)

    orchestrator = create_orchestrator(client)
    coder = create_coder(client)
    reviewer = create_reviewer(client)
    researcher = create_researcher(client)
    architect = create_architect(client)
    tester = create_tester(client)
    writer = create_writer(client)
    devops = create_devops(client)

    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(config.max_turns)

    team = SelectorGroupChat(
        participants=[
            orchestrator,
            coder,
            reviewer,
            researcher,
            architect,
            tester,
            writer,
            devops,
        ],
        model_client=client,
        termination_condition=termination,
        selector_prompt=SELECTOR_PROMPT,
    )
    return team
