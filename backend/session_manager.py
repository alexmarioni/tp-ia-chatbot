from datetime import datetime
from dataclasses import dataclass, field


MAX_CHITCHATS = 3


@dataclass
class SessionData:
    last_active: datetime = field(default_factory=datetime.utcnow)
    warned: bool = False
    active: bool = True
    chitchat_count: int = 0


_sessions: dict[str, SessionData] = {}


def get_or_create(session_id: str) -> SessionData:
    if session_id not in _sessions:
        _sessions[session_id] = SessionData()
    return _sessions[session_id]


def touch(session_id: str) -> None:
    session = get_or_create(session_id)
    session.last_active = datetime.utcnow()
    session.warned = False


def close_session(session_id: str) -> None:
    if session_id in _sessions:
        _sessions[session_id].active = False


def is_active(session_id: str) -> bool:
    return _sessions.get(session_id, SessionData()).active


def increment_chitchat(session_id: str) -> int:
    """Incrementa el contador y retorna el nuevo valor."""
    session = get_or_create(session_id)
    session.chitchat_count += 1
    return session.chitchat_count
