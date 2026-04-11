from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

import autogen_api_agent.session as session_module
from autogen_api_agent.session import Session, SessionManager


class FrozenDateTime(datetime):
    current = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    @classmethod
    def now(cls, tz: timezone | None = None) -> datetime:
        if tz is None:
            return cls.current.replace(tzinfo=None)
        return cls.current.astimezone(tz)


def test_session_tracks_history_and_last_active() -> None:
    session = Session("session-1")

    assert session.session_id == "session-1"
    assert session.history == []
    assert session.last_active >= session.created_at


def test_session_add_message_appends_to_history() -> None:
    session = Session("session-1")

    session.add_message("user", "hello")

    assert session.history == [{"role": "user", "content": "hello"}]


def test_session_is_expired_returns_false_for_fresh_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FrozenDateTime.current = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(session_module, "datetime", FrozenDateTime)
    session = Session("session-1", ttl_minutes=60)

    FrozenDateTime.current = datetime(2024, 1, 1, 12, 30, 0, tzinfo=timezone.utc)

    assert session.is_expired is False


def test_session_is_expired_returns_true_after_ttl(monkeypatch: pytest.MonkeyPatch) -> None:
    FrozenDateTime.current = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(session_module, "datetime", FrozenDateTime)
    session = Session("session-1", ttl_minutes=60)

    FrozenDateTime.current = datetime(2024, 1, 1, 13, 1, 0, tzinfo=timezone.utc)

    assert session.is_expired is True


def test_session_clear_empties_history() -> None:
    session = Session("session-1")
    session.add_message("user", "hello")

    session.clear()

    assert session.history == []


@pytest.mark.asyncio
async def test_session_manager_get_or_create_creates_new_session() -> None:
    manager = SessionManager()

    session = await manager.get_or_create()

    assert isinstance(session, Session)
    assert session.session_id


@pytest.mark.asyncio
async def test_session_manager_get_or_create_returns_existing_session() -> None:
    manager = SessionManager()

    first = await manager.get_or_create("session-1")
    second = await manager.get_or_create("session-1")

    assert first is second


@pytest.mark.asyncio
async def test_session_manager_get_or_create_replaces_expired_session() -> None:
    manager = SessionManager(ttl_minutes=60)
    expired = await manager.get_or_create("session-1")
    expired.last_active = datetime.now(timezone.utc) - timedelta(minutes=61)

    replacement = await manager.get_or_create("session-1")

    assert replacement is not expired
    assert replacement.session_id == "session-1"


@pytest.mark.asyncio
async def test_session_manager_get_returns_none_for_unknown_id() -> None:
    manager = SessionManager()

    assert await manager.get("missing") is None


@pytest.mark.asyncio
async def test_session_manager_delete_removes_session() -> None:
    manager = SessionManager()
    await manager.get_or_create("session-1")

    deleted = await manager.delete("session-1")

    assert deleted is True
    assert await manager.get("session-1") is None


@pytest.mark.asyncio
async def test_session_manager_cleanup_expired_removes_only_expired_sessions() -> None:
    manager = SessionManager(ttl_minutes=60)
    expired = await manager.get_or_create("expired")
    fresh = await manager.get_or_create("fresh")
    expired.last_active = datetime.now(timezone.utc) - timedelta(minutes=61)

    removed = await manager.cleanup_expired()

    assert removed == 1
    assert await manager.get("expired") is None
    assert await manager.get("fresh") is fresh


@pytest.mark.asyncio
async def test_session_manager_list_sessions_excludes_expired() -> None:
    manager = SessionManager(ttl_minutes=60)
    expired = await manager.get_or_create("expired")
    await manager.get_or_create("fresh")
    expired.last_active = datetime.now(timezone.utc) - timedelta(minutes=61)

    sessions = await manager.list_sessions()

    assert sessions == ["fresh"]
