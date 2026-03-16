from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.config.settings import settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def validate_question(question: str) -> str:
    # Check empty
    if not question or not question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    # Check length
    if len(question) > settings.MAX_QUESTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Question too long. Maximum {settings.MAX_QUESTION_LENGTH} characters allowed"
        )

    # Detect prompt injection attempts
    injection_patterns = [
        "ignore all instructions",
        "ignore previous instructions",
        "disregard your instructions",
        "you are now",
        "pretend you are",
        "act as if",
        "forget everything",
        "new instructions:",
        "system prompt:",
    ]

    question_lower = question.lower()
    for pattern in injection_patterns:
        if pattern in question_lower:
            raise HTTPException(
                status_code=400,
                detail="Invalid input detected. Please ask a genuine legal question."
            )

    return question.strip()

def validate_pdf(filename: str, file_size: int) -> None:
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    max_size = settings.MAX_PDF_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.MAX_PDF_SIZE_MB}MB"
        )