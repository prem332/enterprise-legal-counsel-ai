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


def call_llm_with_delay(prompt: str, delay: int = 5) -> str:
    """Call LLM with delay to avoid rate limits."""
    time.sleep(delay)
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()


def score_faithfulness(answer: str, context: str) -> float:
    """
    Faithfulness: Is the answer grounded in the context?
    Score 1.0 if answer is supported by context, 0.0 if not.
    """
    prompt = f"""You are an evaluator. Check if the answer is 
supported by the given context.

Context: {context}

Answer: {answer}

Is every claim in the answer supported by the context?
Reply with only a number between 0 and 1.
1.0 = fully supported by context
0.5 = partially supported
0.0 = not supported at all

Reply with ONLY the number, nothing else."""

    try:
        result = call_llm_with_delay(prompt, delay=5)
        score = float(result.strip())
        return min(max(score, 0.0), 1.0)
    except Exception as e:
        print(f"    Faithfulness error: {e}")
        return 0.0


def score_answer_relevancy(question: str, answer: str) -> float:
    """
    Answer Relevancy: Does the answer address the question?
    Score 1.0 if fully relevant, 0.0 if not relevant.
    """
    prompt = f"""You are an evaluator. Check if the answer 
is relevant to the question.

Question: {question}

Answer: {answer}

How relevant is the answer to the question?
Reply with only a number between 0 and 1.
1.0 = perfectly answers the question
0.5 = partially answers
0.0 = does not answer the question

Reply with ONLY the number, nothing else."""

    try:
        result = call_llm_with_delay(prompt, delay=5)
        score = float(result.strip())
        return min(max(score, 0.0), 1.0)
    except Exception as e:
        print(f"    Relevancy error: {e}")
        return 0.0


def run_ragas_evaluation(pdf_path: str):
    print("Starting Manual RAGAS Evaluation for LexAI...")
    print(f"PDF: {pdf_path}")
    print(f"Questions: {len(TEST_QUESTIONS)}")
    print("-" * 50)

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

    for i, (question, ground_truth) in enumerate(
        zip(TEST_QUESTIONS, GROUND_TRUTHS)
    ):
        print(f"Question {i+1}/{len(TEST_QUESTIONS)}:")
        print(f"  Q: {question}")

        # Get RAG answer
        try:
            rag_result = pipeline.query_rag(question=question)
            answer = rag_result.get("answer", "")

            # Clean answer
            if "\n\n Sources:" in answer:
                answer = answer.split("\n\n Sources:")[0]
            if "Legal Disclaimer" in answer:
                answer = answer.split("Legal Disclaimer")[0]
            answer = answer.strip()

            # Get context
            citations = rag_result.get("citations", [])
            context = " ".join([
                str(c.get("text", ""))
                for c in citations if c.get("text")
            ]) if citations else "No context retrieved"

            print(f"  A: {answer[:100]}...")

        except Exception as e:
            print(f"  RAG Error: {e}")
            answer = "Error occurred"
            context = "No context"

        # Score faithfulness
        print(f"  Scoring faithfulness...")
        faith_score = score_faithfulness(answer, context)
        faithfulness_scores.append(faith_score)
        print(f"  Faithfulness: {faith_score:.3f}")

        # Score relevancy
        print(f"  Scoring relevancy...")
        rel_score = score_answer_relevancy(question, answer)
        relevancy_scores.append(rel_score)
        print(f"  Relevancy: {rel_score:.3f}")

        print()

        # Wait between questions
        if i < len(TEST_QUESTIONS) - 1:
            print(f"  Waiting 5 seconds before next question...")
            print()
            time.sleep(5)

    # Calculate final scores
    avg_faithfulness = sum(faithfulness_scores) / len(faithfulness_scores)
    avg_relevancy = sum(relevancy_scores) / len(relevancy_scores)

    print("=" * 50)
    print("RAGAS EVALUATION RESULTS - LexAI")
    print("=" * 50)
    print(f"Faithfulness:      {avg_faithfulness:.3f}")
    print(f"Answer Relevancy:  {avg_relevancy:.3f}")
    print(f"Questions Tested:  {len(TEST_QUESTIONS)}")
    print("=" * 50)

    # Save results
    results = {
        "faithfulness": round(avg_faithfulness, 3),
        "answer_relevancy": round(avg_relevancy, 3),
        "individual_scores": {
            "faithfulness": [round(s, 3) for s in faithfulness_scores],
            "relevancy": [round(s, 3) for s in relevancy_scores],
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