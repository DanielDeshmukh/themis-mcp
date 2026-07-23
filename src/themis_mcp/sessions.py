"""Session management for MCP HTTP transport."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("themis_mcp")


@dataclass
class Session:
    """A single MCP session."""

    session_id: str
    created_at: float = field(default_factory=time.monotonic)
    last_active: float = field(default_factory=time.monotonic)
    metadata: dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        """Update last active time."""
        self.last_active = time.monotonic()

    def is_expired(self, timeout: float) -> bool:
        """Check if session has expired."""
        return (time.monotonic() - self.last_active) > timeout


class SessionManager:
    """Manage MCP sessions for HTTP transport."""

    def __init__(self, timeout: float = 3600.0) -> None:
        """Initialize session manager.

        Args:
            timeout: Session timeout in seconds (default: 1 hour)
        """
        self.timeout = timeout
        self._sessions: dict[str, Session] = {}

    def create_session(self, metadata: dict[str, Any] | None = None) -> Session:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        session = Session(session_id=session_id, metadata=metadata or {})
        self._sessions[session_id] = session
        logger.info(f"Created session {session_id}")
        return session

    def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID, returns None if not found or expired."""
        session = self._sessions.get(session_id)
        if session is None:
            return None

        if session.is_expired(self.timeout):
            del self._sessions[session_id]
            logger.info(f"Session {session_id} expired")
            return None

        session.touch()
        return session

    def remove_session(self, session_id: str) -> bool:
        """Remove a session. Returns True if session existed."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Removed session {session_id}")
            return True
        return False

    def cleanup_expired(self) -> int:
        """Remove all expired sessions. Returns number of sessions removed."""
        expired = [
            sid
            for sid, session in self._sessions.items()
            if session.is_expired(self.timeout)
        ]
        for sid in expired:
            del self._sessions[sid]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
        return len(expired)

    @property
    def active_count(self) -> int:
        """Number of active sessions."""
        return len(self._sessions)

    @property
    def stats(self) -> dict[str, Any]:
        """Session statistics."""
        return {
            "active_sessions": self.active_count,
            "timeout_seconds": self.timeout,
        }


# Global session manager
session_manager = SessionManager()
