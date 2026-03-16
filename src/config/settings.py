from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama3-8b-8192"

    HF_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    ENVIRONMENT: str = "local"

    CHROMA_PATH: str = "./chroma_db"

    # Vector DB - Production
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_USER_INDEX: str = "user-documents"

    # RAG Config
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5
    SCORE_THRESHOLD: float = 0.5

    # Memory
    MAX_HISTORY: int = 10

    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_PROJECT: str = "enterprise-legal-counsel-ai"

    # Security
    MAX_REQUESTS_PER_MINUTE: int = 10
    MAX_QUESTION_LENGTH: int = 500
    MAX_PDF_SIZE_MB: int = 20

    class Config:
        env_file = ".env"

settings = Settings()