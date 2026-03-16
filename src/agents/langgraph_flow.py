from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from src.config.settings import settings
from src.rag.pipeline import query_rag
from src.rag import pipeline
from typing import TypedDict, Optional

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
    final_answer: str
    citations: list
    needs_suggestion: bool

def query_analyzer_agent(state: LegalState) -> LegalState:
    question = state["question"]

    prompt = f"""Analyze this legal question and respond in exactly this format:
INTENT: [info OR suggestion]
DOMAIN: [criminal OR property OR labour OR consumer OR contract OR constitutional OR general]

Rules:
- intent=suggestion if question contains: reduce, challenge, avoid, fight, how to escape, can I get out
- intent=info for all other questions
- Pick the most relevant domain

Question: {question}

Response:"""

    response = llm.invoke([HumanMessage(content=prompt)])
    lines = response.content.strip().split("\n")

    intent = "info"
    domain = "general"

    for line in lines:
        if "INTENT:" in line:
            intent = line.split(":")[1].strip().lower()
        if "DOMAIN:" in line:
            domain = line.split(":")[1].strip().lower()

    state["intent"] = intent
    state["legal_domain"] = domain
    return state


def legal_researcher_agent(state: LegalState) -> LegalState:
    if not pipeline.pdf_uploaded:
        state["rag_answer"] = ""
        state["citations"] = []
        return state

    try:
        result = query_rag(
            question=state["question"],
            session_id=state["session_id"]
        )
        state["rag_answer"] = result["answer"]
        state["citations"] = result["citations"]
    except Exception as e:
        state["rag_answer"] = ""
        state["citations"] = []

    return state

def law_checker_agent(state: LegalState) -> LegalState:
    question = state["question"]
    domain = state["legal_domain"]
    intent = state["intent"]

    if intent == "suggestion":
        prompt = f"""You are an expert Indian legal advisor specializing in {domain} law.

The user wants to know their legal options regarding:
{question}

Provide:
1. What Indian law says about this
2. Legal options available to the user
3. Specific law sections that support their case
4. Practical steps they can take

Always cite specific sections of Indian law.
Be clear and helpful."""
    else:
        prompt = f"""You are an expert Indian legal advisor specializing in {domain} law.

Answer this legal question using Indian law:
{question}

Always:
1. Cite specific Indian law sections
2. Explain in simple language
3. Give practical guidance"""

    response = llm.invoke([HumanMessage(content=prompt)])
    state["law_answer"] = response.content
    state["needs_suggestion"] = (intent == "suggestion")
    return state

def response_generator_agent(state: LegalState) -> LegalState:
    rag_answer = state.get("rag_answer", "")
    law_answer = state.get("law_answer", "")
    needs_suggestion = state.get("needs_suggestion", False)

    if rag_answer and law_answer:
        # Both PDF and law knowledge available
        final = f"""**From Your Document:**
{rag_answer}

**Indian Law Perspective:**
{law_answer}"""

    elif rag_answer:
        final = rag_answer

    else:
        final = law_answer

    if needs_suggestion:
        final += "\n\n**Important:** These are legal options available to you. Evaluate each carefully with a qualified lawyer."

    state["final_answer"] = final
    return state

def build_legal_graph():
    workflow = StateGraph(LegalState)

    # Add all agent nodes
    workflow.add_node("query_analyzer", query_analyzer_agent)
    workflow.add_node("legal_researcher", legal_researcher_agent)
    workflow.add_node("law_checker", law_checker_agent)
    workflow.add_node("response_generator", response_generator_agent)

    # Connect nodes in order
    workflow.set_entry_point("query_analyzer")
    workflow.add_edge("query_analyzer", "legal_researcher")
    workflow.add_edge("legal_researcher", "law_checker")
    workflow.add_edge("law_checker", "response_generator")
    workflow.add_edge("response_generator", END)

    return workflow.compile()

legal_graph = build_legal_graph()

def run_legal_agents(question: str, session_id: str = None) -> dict:
    """
    Main entry point for multi-agent system.
    Called by FastAPI chat endpoint.
    """
    initial_state = LegalState(
        question=question,
        session_id=session_id,
        intent="",
        legal_domain="",
        rag_answer="",
        law_answer="",
        final_answer="",
        citations=[],
        needs_suggestion=False
    )

    result = legal_graph.invoke(initial_state)

    return {
        "answer": result["final_answer"],
        "session_id": session_id,
        "legal_domain": result["legal_domain"],
        "intent": result["intent"],
        "citations": result["citations"],
        "needs_suggestion": result["needs_suggestion"]
    }