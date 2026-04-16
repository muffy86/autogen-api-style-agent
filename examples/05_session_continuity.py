"""Example: Session continuity across multiple interactions."""

import asyncio

from autogen_api_agent.config import AppConfig
from autogen_api_agent.models import ChatMessage
from autogen_api_agent.providers.factory import ModelClientFactory
from autogen_api_agent.session import SessionManager
from autogen_api_agent.teams import create_team
from autogen_api_agent.utils import extract_final_response, format_task


async def main() -> None:
    config = AppConfig()
    factory = ModelClientFactory(config)
    sessions = SessionManager(ttl_minutes=60)

    session = await sessions.get_or_create("demo-session-001")
    session.add_message("user", "My name is Alice and I'm building a FastAPI app.")

    team = create_team("quick", factory=factory)
    messages = [
        ChatMessage(role="user", content="My name is Alice and I'm building a FastAPI app.")
    ]
    result = await team.run(task=format_task(messages))
    reply = extract_final_response(result)
    session.add_message("assistant", reply)
    print(f"Turn 1 reply: {reply[:200]}...\n")

    history = session.get_history()
    all_messages = [ChatMessage(role=m["role"], content=m["content"]) for m in history]
    all_messages.append(ChatMessage(role="user", content="What was my name again?"))

    team2 = create_team("quick", factory=factory)
    result2 = await team2.run(task=format_task(all_messages))
    reply2 = extract_final_response(result2)
    print(f"Turn 2 reply (should mention Alice): {reply2[:200]}")

    active = await sessions.list_sessions()
    print(f"\nActive sessions: {active}")


if __name__ == "__main__":
    asyncio.run(main())
