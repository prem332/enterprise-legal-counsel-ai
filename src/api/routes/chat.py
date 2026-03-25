from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.agents.langgraph_flow import run_legal_graph
from src.memory.chat_history import clear_session, get_session_messages
from src.security.rate_limiter import validate_question
from src.logging.session_logger import get_session_stats
from src.rag import pipeline

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class ClearRequest(BaseModel):
    session_id: str

@router.post("/query")
async def chat_query(request: ChatRequest):
    clean_question = validate_question(request.question)

    try:
        result = run_legal_graph(
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
    # Clear conversation memory
    success = clear_session(request.session_id)

    # Reset PDF uploaded state
    pipeline.pdf_uploaded = False
    pipeline.pdf_filename = None

    # Clear all document vectors
    from src.rag.vectorstore import reset_vectorstore
    reset_vectorstore()

    return {
        "cleared": success,
        "session_id": request.session_id,
        "message": "Chat and document cleared successfully"
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