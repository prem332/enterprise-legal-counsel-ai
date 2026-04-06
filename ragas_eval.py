from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from src.rag import pipeline
from src.rag.vectorstore import reset_vectorstore
from src.config.settings import settings
import json
import os
import time


TEST_QUESTIONS = [
    "What is the security deposit amount in my rental agreement?",
    "Can I celebrate Diwali and Holi in my rented apartment?",
    "What is the late payment penalty in my agreement?",
    "Am I allowed to work from home in my rented flat?",
]

GROUND_TRUTHS = [
    "The security deposit amount is Rs. 54,000 which is equivalent to 3 months rent.",
    "Yes, the tenant has the right to celebrate all Indian festivals including Diwali and Holi with reasonable noise levels.",
    "A penalty of Rs. 500 per day will be charged for rent paid after the 10th of the month.",
    "Yes, the tenant is permitted to work from home for professional activities including video calls and online meetings.",
]

llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model_name=settings.GROQ_MODEL,
    temperature=0
)


def call_llm(prompt: str, delay: int = 5) -> str:
    """Call LLM with delay to avoid rate limits."""
    time.sleep(delay)
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


def score_faithfulness(answer: str, context: str) -> float:
    """
    Faithfulness: Is the answer grounded in the context?
    1.0 = fully supported, 0.0 = not supported
    """
    prompt = f"""You are an evaluator checking if an answer 
is supported by the given context.

Context: {context}

Answer: {answer}

Is every claim in the answer supported by the context?
Reply with ONLY a number between 0 and 1.
1.0 = fully supported by context
0.5 = partially supported
0.0 = not supported at all"""

    try:
        result = call_llm(prompt, delay=5)
        return min(max(float(result.strip()), 0.0), 1.0)
    except Exception as e:
        print(f"    Faithfulness error: {e}")
        return 0.0


def score_answer_relevancy(question: str, answer: str) -> float:
    """
    Answer Relevancy: Does the answer address the question?
    1.0 = perfectly relevant, 0.0 = not relevant
    """
    prompt = f"""You are an evaluator checking if an answer 
is relevant to the question asked.

Question: {question}

Answer: {answer}

How relevant is the answer to the question?
Reply with ONLY a number between 0 and 1.
1.0 = perfectly answers the question
0.5 = partially answers
0.0 = does not answer the question"""

    try:
        result = call_llm(prompt, delay=5)
        return min(max(float(result.strip()), 0.0), 1.0)
    except Exception as e:
        print(f"    Relevancy error: {e}")
        return 0.0


def score_context_precision(question: str, context: str) -> float:
    """
    Context Precision: Is the retrieved context relevant to the question?
    1.0 = highly relevant context, 0.0 = irrelevant context
    """
    prompt = f"""You are an evaluator checking if the retrieved 
context is relevant and useful for answering the question.

Question: {question}

Retrieved Context: {context}

How relevant and precise is the context for answering this question?
Reply with ONLY a number between 0 and 1.
1.0 = context is perfectly relevant and useful
0.5 = context is partially relevant
0.0 = context is irrelevant or unhelpful"""

    try:
        result = call_llm(prompt, delay=5)
        return min(max(float(result.strip()), 0.0), 1.0)
    except Exception as e:
        print(f"    Context Precision error: {e}")
        return 0.0


def score_context_recall(ground_truth: str, context: str) -> float:
    """
    Context Recall: Does the context contain the ground truth information?
    1.0 = context has all needed info, 0.0 = context missing needed info
    """
    prompt = f"""You are an evaluator checking if the retrieved 
context contains enough information to arrive at the ground truth answer.

Ground Truth Answer: {ground_truth}

Retrieved Context: {context}

Does the context contain the information needed to produce the ground truth?
Reply with ONLY a number between 0 and 1.
1.0 = context fully contains all needed information
0.5 = context partially contains needed information
0.0 = context is missing the needed information"""

    try:
        result = call_llm(prompt, delay=5)
        return min(max(float(result.strip()), 0.0), 1.0)
    except Exception as e:
        print(f"    Context Recall error: {e}")
        return 0.0


def run_ragas_evaluation(pdf_path: str):
    print("Starting RAGAS Evaluation for LexAI...")
    print(f"PDF: {pdf_path}")
    print(f"Questions: {len(TEST_QUESTIONS)}")
    print(f"Metrics: Faithfulness, Relevancy, Context Precision, Context Recall")
    print("-" * 60)

    # Reset and ingest
    reset_vectorstore()
    pipeline.pdf_uploaded = False

    print("Ingesting document...")
    result = pipeline.ingest_documents(
        [(pdf_path, os.path.basename(pdf_path))]
    )
    print(f"Chunks created: {result['chunks_created']}")
    print()

    faithfulness_scores = []
    relevancy_scores = []
    precision_scores = []
    recall_scores = []

    for i, (question, ground_truth) in enumerate(
        zip(TEST_QUESTIONS, GROUND_TRUTHS)
    ):
        print(f"Question {i+1}/{len(TEST_QUESTIONS)}:")
        print(f"  Q: {question}")

        # Get RAG answer
        try:
            rag_result = pipeline.query_rag(question=question)
            answer = rag_result.get("answer", "")

            if "\n\n Sources:" in answer:
                answer = answer.split("\n\n Sources:")[0]
            if "Legal Disclaimer" in answer:
                answer = answer.split("Legal Disclaimer")[0]
            answer = answer.strip()

            # Get context
            citations = rag_result.get("citations", [])
            context = " ".join([
                str(c.get("chunk_text", ""))
                for c in citations
                if c.get("chunk_text")
            ]) if citations else "No context retrieved"

            print(f"  Context length: {len(context)} chars")


        except Exception as e:
            print(f"  RAG Error: {e}")
            answer = "Error occurred"
            context = "No context"

        # Score all 4 metrics
        print(f"  Scoring faithfulness...")
        faith = score_faithfulness(answer, context)
        faithfulness_scores.append(faith)
        print(f"  Faithfulness:      {faith:.3f}")

        print(f"  Scoring relevancy...")
        rel = score_answer_relevancy(question, answer)
        relevancy_scores.append(rel)
        print(f"  Answer Relevancy:  {rel:.3f}")

        print(f"  Scoring context precision...")
        prec = score_context_precision(question, context)
        precision_scores.append(prec)
        print(f"  Context Precision: {prec:.3f}")

        print(f"  Scoring context recall...")
        rec = score_context_recall(ground_truth, context)
        recall_scores.append(rec)
        print(f"  Context Recall:    {rec:.3f}")

        print()

        if i < len(TEST_QUESTIONS) - 1:
            print(f"  Waiting 5 seconds...")
            print()
            time.sleep(5)

    # Calculate averages
    avg_faith = sum(faithfulness_scores) / len(faithfulness_scores)
    avg_rel = sum(relevancy_scores) / len(relevancy_scores)
    avg_prec = sum(precision_scores) / len(precision_scores)
    avg_rec = sum(recall_scores) / len(recall_scores)

    print("=" * 60)
    print("RAGAS EVALUATION RESULTS - LexAI")
    print("=" * 60)
    print(f"Faithfulness:      {avg_faith:.3f}")
    print(f"Answer Relevancy:  {avg_rel:.3f}")
    print(f"Context Precision: {avg_prec:.3f}")
    print(f"Context Recall:    {avg_rec:.3f}")
    print("=" * 60)

    # Save results
    results = {
        "faithfulness": round(avg_faith, 3),
        "answer_relevancy": round(avg_rel, 3),
        "context_precision": round(avg_prec, 3),
        "context_recall": round(avg_rec, 3),
        "individual_scores": {
            "faithfulness": [round(s, 3) for s in faithfulness_scores],
            "relevancy": [round(s, 3) for s in relevancy_scores],
            "context_precision": [round(s, 3) for s in precision_scores],
            "context_recall": [round(s, 3) for s in recall_scores],
        },
        "questions_tested": len(TEST_QUESTIONS),
        "model": settings.GROQ_MODEL,
        "chunk_size": settings.CHUNK_SIZE,
        "chunk_overlap": settings.CHUNK_OVERLAP,
        "top_k": settings.TOP_K,
        "score_threshold": settings.SCORE_THRESHOLD,
        "reranking": "FlashrankRerank top_n=4"
    }

    with open("ragas_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nSaved to ragas_results.json!")
    print("Add these scores to README.md!")
    return results


if __name__ == "__main__":
    PDF_PATH = "tests/data/Indian_Rental_Agreement_v2.pdf"

    if not os.path.exists(PDF_PATH):
        print(f"PDF not found at {PDF_PATH}")
        print("Run: mkdir -p tests/data")
        print("Then copy your PDF there!")
    else:
        run_ragas_evaluation(PDF_PATH)