import json
import os
from datetime import datetime
from typing import Optional

LOG_DIR = "/tmp/session_logs" if os.environ.get("ENVIRONMENT") == "production" else "session_logs"

def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

def log_interaction(
    session_id: str,
    user_query: str,
    bot_response: str,
    response_time_ms: float,
    tokens_used: Optional[int] = None,
    citations_count: int = 0,
    vector_db_used: str = "unknown",
    pdf_uploaded: bool = False,
    pdf_name: Optional[str] = None,
    error: Optional[str] = None
):
    ensure_log_dir()

    log_entry = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "user_query": user_query[:500],
        "bot_response": bot_response[:1000],
        "response_time_ms": round(response_time_ms, 2),
        "tokens_used": tokens_used,
        "citations_count": citations_count,
        "vector_db_used": vector_db_used,
        "pdf_uploaded": pdf_uploaded,
        "pdf_name": pdf_name,
        "error": error
    }

    log_file = os.path.join(LOG_DIR, f"{session_id}.json")

    existing_logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            existing_logs = json.load(f)

    existing_logs.append(log_entry)

    with open(log_file, "w") as f:
        json.dump(existing_logs, f, indent=2)

def get_session_logs(session_id: str) -> list:
    log_file = os.path.join(LOG_DIR, f"{session_id}.json")
    if not os.path.exists(log_file):
        return []
    with open(log_file, "r") as f:
        return json.load(f)

def get_session_stats(session_id: str) -> dict:
    logs = get_session_logs(session_id)
    if not logs:
        return {}

    response_times = [log["response_time_ms"] for log in logs]
    citations = [log["citations_count"] for log in logs]

    return {
        "session_id": session_id,
        "total_queries": len(logs),
        "avg_response_time_ms": round(
            sum(response_times) / len(response_times), 2
        ),
        "total_citations_found": sum(citations),
        "pdf_uploaded": any(l["pdf_uploaded"] for l in logs),
        "errors_count": sum(
            1 for log in logs if log["error"] is not None
        )
    }