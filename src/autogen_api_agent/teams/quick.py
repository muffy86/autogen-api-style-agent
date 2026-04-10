from __future__ import annotations

from autogen_agentchat.agents import AssistantAgent

from ..agents.base import get_tools
from ..config import AppConfig, get_config
from ..providers.factory import ModelClientFactory

QUICK_SYSTEM_MESSAGE = """\
You are a versatile AI assistant with access to file operations, web search, GitHub, \
shell commands, and code analysis tools.

You handle tasks directly and efficiently:
- Write and edit code with proper error handling and type hints.
- Search the web for information and summarize findings.
- Analyze code structure, complexity, and quality.
- Execute shell commands and report results.
- Read, write, and search through files and directories.
- Interact with GitHub repositories, issues, and pull requests.

Workflow:
1. Understand the task clearly.
2. Use the appropriate tools to gather information or make changes.
3. Provide clear, complete responses with working code or actionable results.
4. Say TERMINATE when the task is fully complete.

Rules:
- Be direct and efficient — this is single-agent mode for quick tasks.
- Provide complete solutions, not partial ones.
- Show your reasoning for non-trivial decisions.
- Always verify your work when possible.\
"""


def create_quick_agent(
    factory: ModelClientFactory,
    provider: str | None = None,
    model: str | None = None,
    config: AppConfig | None = None,
) -> AssistantAgent:
    """Create a single all-purpose agent for quick tasks."""
    config = config or get_config()
    client = factory.create(provider, model)

    all_tools = get_tools(
        "file_ops",
        "web_search",
        "github",
        "shell",
        "code_analysis",
    )

    return AssistantAgent(
        name="assistant",
        model_client=client,
        tools=all_tools,
        system_message=QUICK_SYSTEM_MESSAGE,
        description="Versatile single agent with all tools for quick tasks.",
    )
