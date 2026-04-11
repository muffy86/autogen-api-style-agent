"""Example: 3-agent code review team (coder + reviewer + architect)."""

import asyncio

from autogen_api_agent.config import AppConfig
from autogen_api_agent.providers.factory import ModelClientFactory
from autogen_api_agent.teams import create_team

CODE_TO_REVIEW = """
def process_users(db_conn, user_ids):
    results = []
    for uid in user_ids:
        row = db_conn.execute(f"SELECT * FROM users WHERE id = {uid}").fetchone()
        results.append(dict(row))
    return results
"""


async def main() -> None:
    config = AppConfig()
    factory = ModelClientFactory(config)

    team = create_team("code_review", factory=factory)

    result = await team.run(
        task=(
            "Review this Python code for bugs, security issues, and design problems:\n\n"
            f"{CODE_TO_REVIEW}\n\n"
            "Say TERMINATE when complete."
        )
    )
    for msg in result.messages:
        if (
            hasattr(msg, "source")
            and hasattr(msg, "content")
            and isinstance(msg.content, str)
            and "TERMINATE" not in msg.content
        ):
            print(f"\n{'=' * 40}\n[{msg.source}]\n{msg.content}")


if __name__ == "__main__":
    asyncio.run(main())
