"""Example: 3-agent research team with streaming output (researcher + writer + architect)."""

import asyncio

from autogen_api_agent.config import AppConfig
from autogen_api_agent.providers.factory import ModelClientFactory
from autogen_api_agent.teams import create_team
from autogen_api_agent.utils import extract_message_text


async def main() -> None:
    config = AppConfig()
    factory = ModelClientFactory(config)

    team = create_team("research", factory=factory)

    print("Streaming research results...\n")
    async for message in team.run_stream(
        task=(
            "Research the key differences between AutoGen and CrewAI for multi-agent "
            "systems. Say TERMINATE when done."
        )
    ):
        text = extract_message_text(message)
        if text:
            print(text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
