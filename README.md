# ⚖️ Enterprise Legal Counsel AI (LexAI)
Production-grade Indian Legal AI Assistant powered by Multi-Agent RAG, LLaMA 3, LangChain and LangGraph

---

## 🎬 Video Demo
[Watch Full Demo on Google Drive](https://drive.google.com/file/d/1gVa_exEwT7lQq_dHZTxf5Z-O0JxPzzfz/view?usp=drive_link)

> Demo covers: Problem statement, security features, general legal queries, PDF document analysis, RAG pipeline explanation, RAGAS evaluation results and LangSmith monitoring.

---

## 🌐 Live Demo
https://enterprise-legal-counsel-ai.duckdns.org

> **Note:** The live deployment may be temporarily unavailable as AWS EC2 resources are stopped between sessions to manage cloud costs. The full working demo is available in the video above. The complete source code, architecture and evaluation results are documented below.

---

## 🎯 Project Overview
Enterprise Legal Counsel AI (LexAI) is a production-grade AI-powered legal assistant that helps Indian citizens understand their legal rights and analyse legal documents through natural conversation. It addresses the critical gap where 1.4 billion Indians have access to only 1.7 million lawyers, making legal consultation unaffordable for most citizens.

### Two Interaction Modes
- **Document Mode** → Upload any legal PDF (contracts, NDAs, rental agreements, FIRs) and ask specific questions about it
- **Query Mode** → Ask any Indian legal question without uploading a document

---

## 🏗️ Architecture

### High-Level System Architecture
```
User Browser
     ↓
DuckDNS (Free Domain)
     ↓
Nginx (HTTPS Reverse Proxy - Let's Encrypt SSL)
     ↓
FastAPI REST API
├── Rate Limiter (slowapi - 10 req/min)
├── Input Validator (PII detection, harmful intent, injection)
└── Session Manager (UUID per user)
     ↓
LangGraph Multi-Agent Pipeline (StateGraph)
├── Agent 1: Query Analyzer
├── Agent 2: Legal Researcher
├── Agent 3: Law Checker
├── Agent 4: Law Verifier
└── Agent 5: Response Generator
     ↓
LangSmith Monitoring (Traces, Latency, Tokens)
     ↓
React Frontend (Inline JSX, Session Stats, Citations)
```

### Detailed Query Flow
```
Step 1: User submits question
        ↓
        validate_question() in rate_limiter.py
        ├── Empty check
        ├── Length check (max 500 chars)
        ├── Prompt injection detection (26 patterns)
        ├── Harmful intent detection (28 patterns)
        └── PII detection (Aadhaar, PAN, phone, email)
        ↓
Step 2: Agent 1 - Query Analyzer
        ↓ LLM: ChatGroq (llama-3.3-70b-versatile, temperature=0)
        ├── Detects intent: document_query OR general_query
        └── Detects domain: Property/Criminal/Consumer/Labour/Constitutional
        ↓
Step 3: Agent 2 - Legal Researcher
        IF pdf_uploaded = True:
        ├── Stage 1: vectorstore.as_retriever(k=10, search_type=similarity)
        │           ChromaDB (local) or Pinecone (production)
        │           HuggingFace MiniLM embeddings (384-dim vectors)
        ├── Stage 2: FlashrankRerank(top_n=4)
        │           ContextualCompressionRetriever reranks top 10 → top 4
        └── Stage 3: ConversationalRetrievalChain with memory (k=10)
        ELSE: rag_answer = "" (no document mode)
        ↓
Step 4: Agent 3 - Law Checker
        ↓ LLM: ChatGroq (llama-3.3-70b-versatile)
        ├── Uses LLaMA 3 Indian law knowledge
        ├── Cites real law sections (IPC, ICA 1872, Constitution, CPA 2019)
        └── Keeps response under 150 words
        ↓
Step 5: Agent 4 - Law Verifier
        ↓ LLM: ChatGroq (llama-3.3-70b-versatile)
        ├── Compares document answer vs real Indian law
        ├── Outputs: VERIFIED / WARNING / UNVERIFIED
        └── Provides correction if document claim is wrong
        ↓
Step 6: Agent 5 - Response Generator
        ↓ LLM: ChatGroq (llama-3.3-70b-versatile)
        ├── Combines rag_answer + law_answer + verification_status
        ├── Adds verification badge (VERIFIED / WARNING / UNVERIFIED)
        ├── Formats citations with page numbers and relevance scores
        └── Adds legal disclaimer
        ↓
Step 7: Response returned to React frontend
        ├── Session stats updated (queries, citations, avg ms)
        ├── LangSmith trace recorded (latency, tokens, errors)
        └── JSON log saved (session_id, response_time_ms, citations_count)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | LLaMA 3 (llama-3.3-70b-versatile) via Groq API |
| Embeddings | HuggingFace MiniLM (sentence-transformers/all-MiniLM-L6-v2, 384-dim) |
| Orchestration | LangChain + LangGraph (StateGraph) |
| Reranking | FlashrankRerank (ms-marco-MultiBERT-L-12) |
| Vector DB (Local) | ChromaDB |
| Vector DB (Production) | Pinecone (Serverless, us-east-1) |
| API | FastAPI + Uvicorn (async) |
| Frontend | React 18 via CDN + Babel Standalone |
| Monitoring | LangSmith (traces, latency, tokens) |
| Containerization | Docker (python:3.10-slim) |
| CI/CD | GitHub Actions (CI + CD pipelines) |
| Server | AWS EC2 t3.micro (ap-south-1) |
| Reverse Proxy | Nginx (Docker container) |
| SSL | Let's Encrypt via Certbot |
| Domain | DuckDNS (Free subdomain) |
| Container Registry | AWS ECR |

---

## 📊 Evaluation Results

### RAGAS Evaluation
Evaluated using a custom RAGAS-style framework with manual scoring via LLaMA 3 on 4 legal questions using Indian Rental Agreement PDF.

| Metric | Score | Description |
|--------|-------|-------------|
| **Faithfulness** | **1.000** | Every answer grounded in retrieved context - zero hallucination |
| **Answer Relevancy** | **0.950** | Answers directly address the user question |
| **Context Precision** | **0.900** | Retrieved chunks are genuinely relevant (FlashrankRerank working) |
| **Context Recall** | **0.875** | Retrieved chunks contain needed information |

**Evaluation Configuration:**
- Model: llama-3.3-70b-versatile
- Chunk size: 256, Overlap: 80
- Retrieval: Top 10 → FlashrankRerank → Top 4
- Score threshold: 0.25
- Evaluation script: `evaluations/ragas_eval.py`

### LangSmith Production Metrics

| Metric | Value |
|--------|-------|
| P50 Latency | 2.18s |
| P99 Latency | 2.65s |
| Error Rate | 0% |
| Avg Tokens/Query | ~829 |
| Monthly Cost | $0.00 |

### Automated Test Results
- **20/20 tests passing** across 3 levels
- Unit Tests (7): Citations, memory management
- Integration Tests (2): Real PDF ingestion with Pinecone/ChromaDB
- E2E Tests (6): Full API request-response cycle

---

## ✨ Features

### Core AI Features
- 5-agent LangGraph pipeline with single responsibility per agent
- Two-stage retrieval: vector similarity (top 10) → FlashrankRerank (top 4)
- Law Verifier agent cross-checks document claims against real Indian law
- Indian law knowledge: IPC, ICA 1872, Constitution, Consumer Protection Act 2019
- Chat memory with ConversationBufferWindowMemory (k=10 sliding window)

### Security Features
- Prompt injection detection (26 patterns)
- Harmful intent blocking (28 patterns: destroy evidence, bribe, forge, etc.)
- PII detection and rejection (Aadhaar, PAN, phone number, email)
- Rate limiting via slowapi (10 requests/minute per session)
- File validation (PDF only, max 20MB)

### Production Features
- LangSmith monitoring (every LLM call traced)
- Session JSON logging (response_time_ms, citations_count, errors)
- Docker containerization with pre-baked HuggingFace model
- CI/CD via GitHub Actions (CI: test + lint, CD: build + push to ECR)
- HTTPS with automatic SSL renewal via Certbot

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Groq API key (free at console.groq.com)
- Pinecone API key (free tier at app.pinecone.io)
- LangSmith API key (free tier at smith.langchain.com)

### Local Setup
```bash
# Clone repository
git clone https://github.com/prem332/enterprise-legal-counsel-ai.git
cd enterprise-legal-counsel-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
uvicorn src.api.main:app --reload --port 8000
```

Open browser at http://localhost:8000

---

## 🔑 Environment Variables

```env
GROQ_API_KEY=           # Groq API key for LLaMA 3
GROQ_MODEL=             # llama-3.3-70b-versatile
HF_EMBEDDING_MODEL=     # sentence-transformers/all-MiniLM-L6-v2
ENVIRONMENT=            # local or production
PINECONE_API_KEY=       # Pinecone API key
PINECONE_USER_INDEX=    # user-documents
LANGCHAIN_API_KEY=      # LangSmith API key
LANGCHAIN_TRACING_V2=   # true or false
LANGCHAIN_PROJECT=      # enterprise-legal-counsel-ai
CHUNK_SIZE=             # 256
CHUNK_OVERLAP=          # 80
TOP_K=                  # 4
SCORE_THRESHOLD=        # 0.25
MAX_HISTORY=            # 10
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /docs | Swagger UI |
| POST | /api/v1/documents/upload | Upload legal PDF |
| POST | /api/v1/chat/query | Ask legal question |
| POST | /api/v1/chat/clear | Clear chat and reset PDF state |
| GET | /api/v1/chat/history/{id} | Get chat history |
| GET | /api/v1/logs/{session_id} | Get session logs |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v --tb=short

# Run specific level
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

**Test Coverage:**
- Unit Tests (7) → Citations extraction, memory management
- Integration Tests (2) → Real PDF ingestion, vector store operations
- E2E Tests (6) → Full API flow, security validation, error handling
- **Total: 20/20 tests passing ✅**

---

## 🐳 Docker

```bash
# Build image
docker build -t enterprise-legal-counsel-ai .

# Run container
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e PINECONE_API_KEY=your_key \
  enterprise-legal-counsel-ai
```

---

## ☁️ Deployment Architecture

```
GitHub (Code)
     ↓
GitHub Actions CI
├── Python 3.10 setup
├── pip install requirements
├── flake8 linting
├── pytest 20 tests
└── docker build verification
     ↓ (on pass)
GitHub Actions CD
├── Configure AWS credentials
├── Login to ECR
├── docker build + tag
└── docker push to ECR
     ↓
AWS ECR (Container Registry - ap-south-1)
     ↓
AWS EC2 t3.micro (Mumbai - ap-south-1)
├── Docker Container: legal-counsel (port 8000)
│   ├── FastAPI + Uvicorn
│   ├── LangGraph 5-agent pipeline
│   └── HuggingFace MiniLM (pre-baked)
├── Docker Container: nginx-ssl (ports 80, 443)
│   ├── HTTP → HTTPS redirect
│   └── Reverse proxy to port 8000
└── 2GB Swap Space (t3.micro memory optimization)
     ↓
https://enterprise-legal-counsel-ai.duckdns.org
```

---

## 📁 Project Structure

```
enterprise-legal-counsel-ai/
├── src/
│   ├── agents/
│   │   └── langgraph_flow.py      # 5-agent LangGraph StateGraph
│   ├── api/
│   │   ├── main.py                # FastAPI app, CORS, static files
│   │   └── routes/
│   │       ├── chat.py            # /query and /clear endpoints
│   │       ├── documents.py       # /upload endpoint
│   │       └── logs.py            # /logs endpoint
│   ├── config/
│   │   └── settings.py            # Pydantic BaseSettings (.env source of truth)
│   ├── logging/
│   │   └── session_logger.py      # JSON interaction logging
│   ├── memory/
│   │   └── chat_history.py        # ConversationBufferWindowMemory (k=10)
│   ├── rag/
│   │   ├── pipeline.py            # Core RAG: ingest + query_rag
│   │   ├── embeddings.py          # HuggingFace singleton
│   │   ├── vectorstore.py         # ChromaDB/Pinecone/FAISS with reset
│   │   └── citations.py           # Citation extraction and formatting
│   └── security/
│       └── rate_limiter.py        # Injection, PII, harmful intent detection
├── static/
│   ├── index.html                 # React frontend (inline JSX)
│   └── styles.css                 # Dark theme CSS
├── tests/
│   ├── unit/                      # 7 unit tests
│   ├── integration/               # 2 integration tests
│   └── e2e/                       # 6 E2E tests
├── evaluations/
│   ├── ragas_eval.py              # Custom RAGAS evaluation script
│   └── ragas_results.json         # Official evaluation scores
├── results/
│   └── site_screenshots/          # Production site screenshots
├── api_tests/
│   └── lexai.http                 # REST Client test file
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── .github/workflows/
    ├── ci.yml                     # Test + lint on every push
    └── cd.yml                     # Build + push to ECR on main
```

---

## 📈 Monitoring

LangSmith provides full production observability:
- Complete LLM call tracing for all 5 agents
- P50/P99 latency per agent step
- Token usage and cost tracking per session
- Real-time error detection and alerting
- Multi-agent execution graph visualization

---

## ⚠️ Disclaimer

This application provides AI-generated legal information for educational purposes only. This is **NOT legal advice**. Always consult a qualified lawyer before taking any legal action.

---

## 👨‍💻 Developer

**Prem Kumar** | AI/ML Engineer | Hyderabad, India

[![GitHub](https://img.shields.io/badge/GitHub-prem332-black)](https://github.com/prem332)

> Live Project: enterprise-legal-counsel-ai.duckdns.org
