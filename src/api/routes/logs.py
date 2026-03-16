from fastapi import APIRouter, HTTPException
from src.logging.session_logger import get_session_logs, get_session_stats

router = APIRouter()

@router.get("/{session_id}")
async def get_logs(session_id: str):
    logs = get_session_logs(session_id)
    if not logs:
        raise HTTPException(
            status_code=404,
            detail="No logs found for this session"
        )
    return {
        "session_id": session_id,
        "total_interactions": len(logs),
        "logs": logs
    }

@router.get("/stats/{session_id}")
async def get_stats(session_id: str):
    stats = get_session_stats(session_id)
    if not stats:
        raise HTTPException(
            status_code=404,
            detail="No stats found for this session"
        )
    return stats