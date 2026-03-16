from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from src.rag.vectorstore import get_vectorstore
from src.rag.citations import extract_citations, format_citations, format_legal_disclaimer
from src.rag.embeddings import get_embeddings
from src.memory.chat_history import get_or_create_session
from src.logging.session_logger import log_interaction
from src.config.settings import settings
import time
import tempfile
import os

llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,
    temperature=0
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP
)

pdf_uploaded = False
pdf_filename = None

def ingest_documents(files: list) -> dict:
    global pdf_uploaded, pdf_filename
    all_docs = []

    for file_path, filename in files:
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        # Add real filename to metadata for citations
        for doc in docs:
            doc.metadata["source"] = filename

        chunks = text_splitter.split_documents(docs)
        all_docs.extend(chunks)

        pdf_filename = filename

    vectorstore, db_used = get_vectorstore()
    vectorstore.add_documents(all_docs)

    # Save FAISS backup
    faiss_store = FAISS.from_documents(all_docs, get_embeddings())
    faiss_store.save_local("faiss_index")

    pdf_uploaded = True

    return {
        "chunks_created": len(all_docs),
        "documents_processed": len(files),
        "vector_db": db_used,
        "filename": pdf_filename
    }

def query_rag(
    question: str,
    session_id: str = None
) -> dict:
    
    start_time = time.time()

    # Get or create session memory
    session_id, memory = get_or_create_session(session_id)

    try:
        if pdf_uploaded:
            # PDF mode - Hybrid RAG search
            vectorstore, db_used = get_vectorstore()

            semantic_retriever = vectorstore.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={
                    "k": settings.TOP_K,
                    "score_threshold": settings.SCORE_THRESHOLD
                }
            )

            # Build RAG chain
            chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=semantic_retriever,
                memory=memory,
                return_source_documents=True,
                verbose=False
            )

            result = chain.invoke({"question": question})
            source_docs = result.get("source_documents", [])
            docs_with_scores = [(doc, 0.9) for doc in source_docs]
            citations = extract_citations(docs_with_scores)

        else:
            # No PDF mode - Pure LLaMA 3 legal knowledge
            db_used = "none"

            # Add Indian law context to question
            legal_prompt = f"""You are an expert Indian legal advisor.
Answer the following legal question using your knowledge of
Indian laws including IPC, Indian Contract Act 1872,
Consumer Protection Act 2019, Constitution of India,
and other relevant Indian laws.

Always cite specific law sections when answering.
Be clear, accurate and helpful.

Question: {question}"""

            from langchain.schema import HumanMessage
            response = llm.invoke([HumanMessage(content=legal_prompt)])
            result = {"answer": response.content}
            citations = []

        # Format final answer
        citation_text = format_citations(citations)
        disclaimer = format_legal_disclaimer()
        answer = result["answer"] + citation_text + disclaimer

        # Calculate response time
        response_time = (time.time() - start_time) * 1000

        # Log interaction
        log_interaction(
            session_id=session_id,
            user_query=question,
            bot_response=answer,
            response_time_ms=response_time,
            citations_count=len(citations),
            vector_db_used=db_used,
            pdf_uploaded=pdf_uploaded,
            pdf_name=pdf_filename
        )

        return {
            "answer": answer,
            "session_id": session_id,
            "citations": [c.__dict__ for c in citations],
            "vector_db_used": db_used,
            "pdf_mode": pdf_uploaded,
            "response_time_ms": round(response_time, 2)
        }

    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        log_interaction(
            session_id=session_id,
            user_query=question,
            bot_response="Error occurred",
            response_time_ms=response_time,
            error=str(e)
        )
        raise Exception(f"Query failed: {str(e)}")