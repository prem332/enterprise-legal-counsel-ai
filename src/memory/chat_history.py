from langchain.memory import ConversationBufferWindowMemory
from typing import Dict
from src.config.settings import settings
import uuid

# In-memory session store
# Key: session_id, Value: memory object
session_store: Dict[str, ConversationBufferWindowMemory] = {}

def get_or_create_session(session_id: str = None):
    if not session_id:
        session_id = str(uuid.uuid4())

    if session_id not in session_store:
        session_store[session_id] = ConversationBufferWindowMemory(
            k=settings.MAX_HISTORY,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    return session_id, session_store[session_id]

def get_session_messages(session_id: str) -> list:
    if session_id not in session_store:
        return []
    memory = session_store[session_id]
    return memory.chat_memory.messages

def clear_session(session_id: str) -> bool:
    if session_id in session_store:
        del session_store[session_id]
        return True
    return False

def get_active_sessions() -> int:
    return len(session_store)