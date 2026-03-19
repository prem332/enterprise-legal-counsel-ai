# ⚖️ Enterprise Legal Counsel AI

> Production-grade Indian Legal AI Assistant powered by Multi-Agent RAG, LLaMA 3, LangChain and LangGraph

![CI](https://github.com/prem332/enterprise-legal-counsel-ai/actions/workflows/ci.yml/badge.svg)

---

## 🎯 Project Overview

Enterprise Legal Counsel AI is an AI-powered legal assistant that helps Indian citizens understand their legal rights and analyse legal documents through natural conversation.

### Two Interaction Modes:
- **Document Mode** → Upload any legal PDF (contracts, NDAs, FIRs) and ask questions
- **Query Mode** → Ask any Indian legal question without uploading a document

---

## 🏗️ Architecture
```
User Request
      ↓
FastAPI REST API (Rate Limited + Input Validated)
      ↓
LangGraph Multi-Agent System
├── Agent 1: Query Analyzer    → Detects intent and legal domain
├── Agent 2: Legal Researcher  → RAG search on uploaded PDF
├── Agent 3: Law Checker       → LLaMA 3 Indian law knowledge
└── Agent 4: Response Generator → Combines all outputs
      ↓
Streaming Response + Citations
      ↓
React Frontend (Session Stats + Chat History)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | LLaMA 3 via Groq API |
| Embeddings | HuggingFace MiniLM (384d) |
| Orchestration | LangChain + LangGraph |
| Vector DB (Local) | ChromaDB |
| Vector DB (Production) | Pinecone |
| API | FastAPI (REST) |
| Frontend | React via CDN + CSS |
| Monitoring | LangSmith |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Deployment | AWS Lambda + ECR |

---

## ✨ Features

- Multi-Agent RAG pipeline with LangGraph
- Hybrid semantic + keyword search
- Indian law cross-validation (IPC, ICA 1872, Constitution)
- Legal suggestions engine
- PDF upload with 20MB limit enforcement
- Chat memory (k=10 sliding window)
- Session logging with performance metrics
- Rate limiting (10 req/min)
- Prompt injection detection
- Legal disclaimer on every response
- Downloadable session logs

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Groq API key (free)
- Pinecone API key (free tier)
- LangSmith API key (free tier)

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

Open browser at `http://localhost:8000`

---

## 🔑 Environment Variables
```
GROQ_API_KEY=           # Groq API key for LLaMA 3
GROQ_MODEL=             # llama-3.3-70b-versatile
HF_EMBEDDING_MODEL=     # sentence-transformers/all-MiniLM-L6-v2
ENVIRONMENT=            # local or production
PINECONE_API_KEY=       # Pinecone API key
LANGCHAIN_API_KEY=      # LangSmith API key
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |
| POST | `/api/v1/documents/upload` | Upload legal PDF |
| POST | `/api/v1/chat/query` | Ask legal question |
| POST | `/api/v1/chat/clear` | Clear chat session |
| GET | `/api/v1/chat/history/{id}` | Get chat history |
| GET | `/api/v1/logs/{session_id}` | Get session logs |

---

## 🧪 Testing
```bash
# Run all tests
pytest tests/ -v --tb=short

# Run specific test level
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

### Test Coverage:
- Unit Tests (7) → Citations, Memory
- Integration Tests (2) → Real PDF ingestion
- E2E Tests (6) → Full API flow

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

## 📁 Project Structure
```
enterprise-legal-counsel-ai/
├── src/
│   ├── agents/          # LangGraph multi-agent system
│   ├── api/             # FastAPI routes and main app
│   ├── config/          # Settings and configuration
│   ├── logging/         # Session interaction logging
│   ├── memory/          # Chat history management
│   ├── rag/             # RAG pipeline, embeddings, citations
│   └── security/        # Rate limiting, input validation
├── static/              # React frontend
├── tests/
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests with real PDFs
│   └── e2e/             # End-to-end API tests
├── api_tests/           # REST Client .http test file
├── Dockerfile
├── requirements.txt
└── .github/workflows/   # CI/CD pipelines
```