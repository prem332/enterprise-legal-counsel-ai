from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.agents.langgraph_flow import run_legal_agents
from src.memory.chat_history import clear_session, get_session_messages
from src.security.rate_limiter import validate_question
from src.logging.session_logger import get_session_stats
import json

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ClearRequest(BaseModel):
    session_id: str

@router.post("/query")
async def chat_query(request: ChatRequest):
    # Validate and sanitize input
    clean_question = validate_question(request.question)

    try:
        # Run through LangGraph agents
        result = run_legal_agents(
            question=clean_question,
            session_id=request.session_id
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )

@router.post("/clear")
async def clear_chat(request: ClearRequest):
    success = clear_session(request.session_id)
    return {
        "cleared": success,
        "session_id": request.session_id,
        "message": "Chat cleared successfully" if success else "Session not found"
    }

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    messages = get_session_messages(session_id)
    return {
        "session_id": session_id,
        "messages": [
            {
                "type": msg.type,
                "content": msg.content
            }
            for msg in messages
        ]
    }

@router.get("/stats/{session_id}")
async def get_chat_stats(session_id: str):
    stats = get_session_stats(session_id)
    if not stats:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    return stats