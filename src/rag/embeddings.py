from langchain_huggingface import HuggingFaceEmbeddings
from src.config.settings import settings

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=settings.HF_EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )