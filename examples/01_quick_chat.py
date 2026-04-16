"""Example: Quick single-agent chat using the "quick" team."""

import asyncio

from autogen_api_agent.config import AppConfig
from autogen_api_agent.providers.factory import ModelClientFactory
from autogen_api_agent.teams import create_team


async def main() -> None:
    config = AppConfig()
    factory = ModelClientFactory(config)

    agent = create_team("quick", factory=factory)

    result = await agent.run(task="Write a Python function to calculate fibonacci numbers.")
    for msg in result.messages:
        if hasattr(msg, "content") and isinstance(msg.content, str):
            print(f"[{msg.source}]: {msg.content[:200]}")


if __name__ == "__main__":
    asyncio.run(main())
