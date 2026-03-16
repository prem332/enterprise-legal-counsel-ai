from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma
from src.rag.embeddings import get_embeddings
from src.config.settings import settings
import os

embeddings = get_embeddings()

def get_chroma_store():
    return Chroma(
        collection_name="legal-documents",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PATH
    )

def get_pinecone_store():
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone, ServerlessSpec

    pc = Pinecone(api_key=settings.PINECONE_API_KEY)

    if settings.PINECONE_USER_INDEX not in pc.list_indexes().names():
        pc.create_index(
            name=settings.PINECONE_USER_INDEX,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    return PineconeVectorStore(
        index_name=settings.PINECONE_USER_INDEX,
        embedding=embeddings
    )

def get_faiss_store():
    faiss_path = "faiss_index"
    if os.path.exists(faiss_path):
        return FAISS.load_local(
            faiss_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
    return None

def get_vectorstore():
    if settings.ENVIRONMENT == "local":
        try:
            return get_chroma_store(), "chroma"
        except Exception as e:
            print(f"ChromaDB failed: {e}. Trying FAISS.")
            faiss = get_faiss_store()
            if faiss:
                return faiss, "faiss"
            raise Exception("ChromaDB and FAISS both unavailable!")
    else:
        try:
            return get_pinecone_store(), "pinecone"
        except Exception as e:
            print(f"Pinecone failed: {e}. Trying FAISS.")
            faiss = get_faiss_store()
            if faiss:
                return faiss, "faiss"
            raise Exception("Pinecone and FAISS both unavailable!")