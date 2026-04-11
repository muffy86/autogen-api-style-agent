from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timedelta, timezone


class Session:
    """A conversation session with message history and TTL."""

    def __init__(self, session_id: str, ttl_minutes: int = 60):
        self.session_id = session_id
        self.history: list[dict[str, str]] = []
        self.created_at = datetime.now(timezone.utc)
        self.last_active = datetime.now(timezone.utc)
        self.ttl = timedelta(minutes=ttl_minutes)

    @property
    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) - self.last_active > self.ttl

    def add_message(self, role: str, content: str) -> None:
        self.last_active = datetime.now(timezone.utc)
        self.history.append({"role": role, "content": content})

    def get_history(self) -> list[dict[str, str]]:
        return list(self.history)

    def clear(self) -> None:
        self.history.clear()
        self.last_active = datetime.now(timezone.utc)


class SessionManager:
    """Thread-safe session storage with TTL-based cleanup."""

    def __init__(self, ttl_minutes: int = 60):
        self._sessions: dict[str, Session] = {}
        self._lock = asyncio.Lock()
        self.ttl_minutes = ttl_minutes

    async def get_or_create(self, session_id: str | None = None) -> Session:
        async with self._lock:
            if session_id and session_id in self._sessions:
                session = self._sessions[session_id]
                if not session.is_expired:
                    return session
                del self._sessions[session_id]

            new_id = session_id or uuid.uuid4().hex
            session = Session(new_id, self.ttl_minutes)
            self._sessions[new_id] = session
            return session

    async def get(self, session_id: str) -> Session | None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session and not session.is_expired:
                return session
            if session:
                del self._sessions[session_id]
            return None

    async def delete(self, session_id: str) -> bool:
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    async def cleanup_expired(self) -> int:
        async with self._lock:
            expired = [sid for sid, s in self._sessions.items() if s.is_expired]
            for sid in expired:
                del self._sessions[sid]
            return len(expired)

    async def cleanup_all(self) -> None:
        """Remove all sessions (used during shutdown)."""
        async with self._lock:
            self._sessions.clear()

    async def list_sessions(self) -> list[str]:
        async with self._lock:
            return [sid for sid, s in self._sessions.items() if not s.is_expired]
