from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from src.config.settings import settings
from src.rag import pipeline

llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,
    temperature=0
)

class LegalState(TypedDict):
    question: str
    session_id: Optional[str]
    intent: str
    legal_domain: str
    rag_answer: str
    law_answer: str
    verification_result: str
    verification_status: str
    final_answer: str
    citations: list

def query_analyzer(state: LegalState) -> LegalState:
    prompt = f"""Analyze this legal question and respond in exactly this format:
INTENT: [document_query OR general_query]
DOMAIN: [Property OR Criminal OR Consumer OR Labour OR Constitutional OR Civil OR Family OR Other]

Question: {state['question']}"""

    response = llm.invoke([HumanMessage(content=prompt)])
    lines = response.content.strip().split('\n')

    intent = "general_query"
    domain = "General"

    for line in lines:
        if line.startswith("INTENT:"):
            intent = line.replace("INTENT:", "").strip()
        elif line.startswith("DOMAIN:"):
            domain = line.replace("DOMAIN:", "").strip()

    state["intent"] = intent
    state["legal_domain"] = domain
    return state

def legal_researcher(state: LegalState) -> LegalState:
    try:
        # Double check PDF is actually uploaded AND has chunks
        if pipeline.pdf_uploaded:
            # Verify ChromaDB actually has documents
            try:
                from src.rag.vectorstore import get_vectorstore
                vectorstore, _ = get_vectorstore()
                count = vectorstore._collection.count()
                if count == 0:
                    # ChromaDB is empty - reset flag!
                    pipeline.pdf_uploaded = False
                    pipeline.pdf_filename = None
            except Exception:
                pipeline.pdf_uploaded = False

        if pipeline.pdf_uploaded:
            result = pipeline.query_rag(
                question=state["question"],
                session_id=state.get("session_id")
            )
            state["rag_answer"] = result.get("answer", "")
            state["citations"] = result.get("citations", [])
        else:
            state["rag_answer"] = ""
            state["citations"] = []
    except Exception:
        state["rag_answer"] = ""
        state["citations"] = []
    return state

def law_checker(state: LegalState) -> LegalState:
    prompt = f"""You are an expert Indian Legal Advisor with deep knowledge of:
- Indian Penal Code (IPC) 1860
- Indian Contract Act (ICA) 1872
- Constitution of India
- Consumer Protection Act 2019
- Transfer of Property Act 1882
- Code of Civil Procedure (CPC)
- All major Indian laws and acts

Question: {state['question']}
Legal Domain: {state['legal_domain']}

Provide a focused answer citing ONLY real Indian law sections.
Keep your answer under 150 words.
Format: Direct answer with specific law sections cited."""

    response = llm.invoke([HumanMessage(content=prompt)])
    state["law_answer"] = response.content.strip()
    return state

def law_verifier(state: LegalState) -> LegalState:
    """
    NEW Agent: Verifies document claims against real Indian law knowledge.
    Flags fake or incorrect law codes in uploaded documents.
    """
    if not state.get("rag_answer") or not pipeline.pdf_uploaded:
        state["verification_result"] = ""
        state["verification_status"] = "NO_DOCUMENT"
        return state

    prompt = f"""You are an Indian Legal Verification Expert.

A document has provided this answer to a legal question:
DOCUMENT ANSWER: {state['rag_answer']}

REAL INDIAN LAW CONTEXT: {state['law_answer']}

Your task: Verify if the document claims are consistent with real Indian law.

Check for:
1. Fake or non-existent law section numbers
2. Incorrect law interpretations
3. Misleading legal claims
4. Fabricated rights or obligations

Respond in EXACTLY this format:
STATUS: [VERIFIED or WARNING or UNVERIFIED]
REASON: [One sentence explanation]
CORRECTION: [Only if STATUS is WARNING or UNVERIFIED - provide correct information]

Be strict but fair. Common real sections: IPC 420, ICA 10-27, Constitution Art 14-32, CPC Order 39."""

    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    status = "VERIFIED"
    reason = ""
    correction = ""

    for line in content.split('\n'):
        if line.startswith("STATUS:"):
            status = line.replace("STATUS:", "").strip()
        elif line.startswith("REASON:"):
            reason = line.replace("REASON:", "").strip()
        elif line.startswith("CORRECTION:"):
            correction = line.replace("CORRECTION:", "").strip()

    state["verification_status"] = status
    state["verification_result"] = f"{reason} {correction}".strip()
    return state

def response_generator(state: LegalState) -> LegalState:
    # Check if RAG actually found document content
    rag_answer = state.get("rag_answer", "").strip()
    has_real_doc_answer = (
        pipeline.pdf_uploaded and
        rag_answer and
        len(rag_answer) > 20 and
        "no specific document" not in rag_answer.lower() and
        "no document" not in rag_answer.lower()
    )

    verification_status = state.get("verification_status", "NO_DOCUMENT")
    verification_result = state.get("verification_result", "")

    if verification_status == "VERIFIED":
        verification_badge = "✅ Document claims verified against Indian law."
    elif verification_status == "WARNING":
        verification_badge = f"⚠️ WARNING: {verification_result}"
    elif verification_status == "UNVERIFIED":
        verification_badge = f"❌ UNVERIFIED: {verification_result}"
    else:
        verification_badge = ""

    if has_real_doc_answer:
        prompt = f"""You are a concise Indian Legal AI Assistant.

The user uploaded a document and asked: {state['question']}

DOCUMENT ANSWER: {rag_answer}
VERIFIED INDIAN LAW: {state['law_answer']}
VERIFICATION STATUS: {verification_status}

Rules:
1. Start with "From Your Document:" 
2. Give document answer in 2-3 sentences MAX
3. If VERIFIED: Confirm briefly
4. If WARNING or UNVERIFIED: State document may be wrong
5. ONE practical tip only
6. Under 120 words total"""

    else:
        # No real document answer - use Indian law only!
        prompt = f"""You are a concise Indian Legal AI Assistant.

Question: {state['question']}
Domain: {state['legal_domain']}
Indian Law Answer: {state['law_answer']}

Rules:
1. Give direct answer in 3-4 sentences MAX
2. Cite 1-2 specific real Indian law sections
3. ONE practical step only
4. Under 100 words
5. Do NOT mention any document"""

    response = llm.invoke([HumanMessage(content=prompt)])
    answer = response.content.strip()

    if verification_badge and has_real_doc_answer:
        answer = f"{answer}\n\n{verification_badge}"

    answer += "\n\n*Legal Disclaimer: AI-generated information for educational purposes only. Not legal advice. Consult a qualified lawyer.*"

    state["final_answer"] = answer
    return state

# Build LangGraph workflow
def build_legal_graph():
    workflow = StateGraph(LegalState)

    # Add all 5 nodes
    workflow.add_node("query_analyzer", query_analyzer)
    workflow.add_node("legal_researcher", legal_researcher)
    workflow.add_node("law_checker", law_checker)
    workflow.add_node("law_verifier", law_verifier)
    workflow.add_node("response_generator", response_generator)

    # Define flow
    workflow.set_entry_point("query_analyzer")
    workflow.add_edge("query_analyzer", "legal_researcher")
    workflow.add_edge("legal_researcher", "law_checker")
    workflow.add_edge("law_checker", "law_verifier")
    workflow.add_edge("law_verifier", "response_generator")
    workflow.add_edge("response_generator", END)

    return workflow.compile()

legal_graph = build_legal_graph()

def run_legal_graph(question: str, session_id: Optional[str] = None) -> dict:
    initial_state = LegalState(
        question=question,
        session_id=session_id,
        intent="",
        legal_domain="",
        rag_answer="",
        law_answer="",
        verification_result="",
        verification_status="",
        final_answer="",
        citations=[]
    )

    result = legal_graph.invoke(initial_state)

    return {
        "answer": result["final_answer"],
        "legal_domain": result["legal_domain"],
        "citations": result["citations"],
        "verification_status": result.get("verification_status", ""),
        "session_id": session_id
    }
