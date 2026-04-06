from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma
from src.rag.embeddings import get_embeddings
from src.config.settings import settings
import os
import chromadb
from chromadb.config import Settings as ChromaSettings

embeddings = get_embeddings()

def get_chroma_store():
    return Chroma(
        collection_name="legal-documents",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PATH,
        client_settings=ChromaSettings(
            anonymized_telemetry=False
        )
    )

def get_pinecone_store():
    from langchain_pinecone import PineconeVectorStore
    from pinecone import Pinecone, ServerlessSpec

    pc = Pinecone(api_key=settings.PINECONE_API_KEY)

    existing = pc.list_indexes().names()
    
    if settings.PINECONE_USER_INDEX in existing:
        index_info = pc.describe_index(settings.PINECONE_USER_INDEX)
        if index_info.dimension != 384:
            print("Dimension mismatch! Deleting and recreating index...")
            pc.delete_index(settings.PINECONE_USER_INDEX)
            existing = []

    if settings.PINECONE_USER_INDEX not in existing:
        pc.create_index(
            name=settings.PINECONE_USER_INDEX,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"Created fresh Pinecone index: {settings.PINECONE_USER_INDEX}")

    return PineconeVectorStore(
        index_name=settings.PINECONE_USER_INDEX,
        embedding=embeddings
    )


def get_faiss_store():
    faiss_path = "/tmp/faiss_index" if settings.ENVIRONMENT == "production" else "faiss_index"
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

def reset_vectorstore():
    """Clears all uploaded document vectors."""
    try:
        if settings.ENVIRONMENT == "local":
            import shutil
            if os.path.exists(settings.CHROMA_PATH):
                shutil.rmtree(settings.CHROMA_PATH)
                print(f"ChromaDB deleted: {settings.CHROMA_PATH}")
        else:
            from pinecone import Pinecone
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            index = pc.Index(settings.PINECONE_USER_INDEX)
            index.delete(delete_all=True)
            print("Pinecone index cleared!")

            import time
            time.sleep(2)
            stats = index.describe_index_stats()
            print(f"Pinecone vector count after clear: {stats.total_vector_count}")

        # Clear FAISS backup
        for faiss_path in ["faiss_index", "/tmp/faiss_index"]:
            if os.path.exists(faiss_path):
                import shutil
                shutil.rmtree(faiss_path)
                print(f"FAISS cleared: {faiss_path}")

        # Reset pipeline flags
        from src.rag import pipeline as p
        p.pdf_uploaded = False
        p.pdf_filename = None
        print("Pipeline flags reset!")

    except Exception as e:
        print(f"Reset warning: {e}")