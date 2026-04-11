"""Example: Full 8-agent productivity team with SelectorGroupChat."""

import asyncio

from autogen_api_agent.config import AppConfig
from autogen_api_agent.providers.factory import ModelClientFactory
from autogen_api_agent.teams import create_team


async def main() -> None:
    config = AppConfig()
    factory = ModelClientFactory(config)

    team = create_team("productivity", factory=factory)

    result = await team.run(
        task=(
            "Design and implement a simple REST API for a todo list app. "
            "Include the FastAPI code, tests, and a README. Say TERMINATE when done."
        )
    )
    for msg in reversed(result.messages):
        if (
            hasattr(msg, "source")
            and msg.source != "user"
            and hasattr(msg, "content")
            and isinstance(msg.content, str)
            and "TERMINATE" not in msg.content
        ):
            print(msg.content)
            break


if __name__ == "__main__":
    asyncio.run(main())
