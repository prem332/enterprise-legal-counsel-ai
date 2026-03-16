import pytest
from src.memory.chat_history import (
    get_or_create_session,
    clear_session,
    get_active_sessions
)

def test_create_new_session():
    """Test new session creation with UUID"""
    session_id, memory = get_or_create_session()
    assert session_id is not None
    assert len(session_id) == 36  # UUID format
    assert memory is not None

def test_existing_session_returned():
    """Test same session returned for same ID"""
    session_id, memory1 = get_or_create_session()
    _, memory2 = get_or_create_session(session_id)
    assert memory1 is memory2

def test_clear_session():
    """Test session deletion"""
    session_id, _ = get_or_create_session()
    result = clear_session(session_id)
    assert result == True

def test_clear_nonexistent_session():
    """Test clearing session that does not exist"""
    result = clear_session("nonexistent-session-id")
    assert result == False

def test_active_sessions_count():
    """Test active session counter"""
    initial = get_active_sessions()
    get_or_create_session()
    assert get_active_sessions() >= initial