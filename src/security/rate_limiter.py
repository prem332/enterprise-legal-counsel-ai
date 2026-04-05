from fastapi import HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.config.settings import settings
import re


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Prompt injection patterns
INJECTION_PATTERNS = [
    "ignore all instructions",
    "ignore previous instructions",
    "disregard your instructions",
    "disregard",
    "you are now",
    "pretend you are",
    "act as if",
    "act as",
    "forget everything",
    "new instructions:",
    "system prompt:",
    "forget all previous",
    "override instructions",
    "simulate being",
    "bypass",
    "jailbreak",
]


# Harmful intent patterns
HARMFUL_PATTERNS = [
    "how to escape",
    "destroy evidence",
    "hide evidence",
    "tamper evidence",
    "delete evidence",
    "plant evidence",
    "destroy proof",
    "bribe judge",
    "bribe police",
    "bribe officer",
    "forge document",
    "forge signature",
    "fake document",
    "fake signature",
    "money laundering",
    "how to kill",
    "how to murder",
    "how to assault",
    "commit fraud",
    "evade arrest",
    "evade police",
    "evade tax illegally",
    "help me commit",
    "illegal way",
    "without getting caught",
    "avoid getting caught",
    "get away with",
    "frame someone",
]


# PII patterns — (regex, description)
PII_PATTERNS = [
    (r'\b\d{12}\b', "Aadhaar number"),
    (r'\b[A-Z]{5}\d{4}[A-Z]\b', "PAN card number"),
    (r'\b\d{10}\b', "phone number"),
    (r'\b[\w.-]+@[\w.-]+\.\w+\b', "email address"),
    (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', "card number"),
]


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

    question_lower = question.lower()

    # Check prompt injection
    for pattern in INJECTION_PATTERNS:
        if pattern in question_lower:
            raise HTTPException(
                status_code=400,
                detail="Invalid input detected. Please ask a genuine legal question."
            )

    # Check harmful intent
    for phrase in HARMFUL_PATTERNS:
        if phrase in question_lower:
            raise HTTPException(
                status_code=400,
                detail=(
                    "This query involves potentially harmful or illegal activity. "
                    "LexAI provides legal guidance for lawful purposes only. "
                    "If you are in danger please contact emergency services."
                )
            )

    # Check PII
    for pattern, pii_type in PII_PATTERNS:
        if re.search(pattern, question):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Please do not share personal information ({pii_type}) "
                    "in your query. Remove sensitive details and try again."
                )
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