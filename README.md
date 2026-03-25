# ⚖️ Enterprise Legal Counsel AI

> Production-grade Indian Legal AI Assistant powered by Multi-Agent RAG, LLaMA 3, LangChain and LangGraph

![CI](https://github.com/prem332/enterprise-legal-counsel-ai/actions/workflows/ci.yml/badge.svg)

## 🌐 Live Demo

**[https://enterprise-legal-counsel-ai.duckdns.org](https://enterprise-legal-counsel-ai.duckdns.org)**

> Deployed on AWS EC2 (ap-south-1) with HTTPS via Let's Encrypt

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
Nginx (HTTPS Reverse Proxy)
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
| LLM | LLaMA 3 (llama-3.3-70b-versatile) via Groq API |
| Embeddings | HuggingFace MiniLM (sentence-transformers/all-MiniLM-L6-v2) |
| Orchestration | LangChain + LangGraph |
| Vector DB (Local) | ChromaDB |
| Vector DB (Production) | Pinecone |
| API | FastAPI (REST) |
| Frontend | React via CDN + CSS |
| Monitoring | LangSmith |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Server | AWS EC2 t3.micro (ap-south-1) |
| Reverse Proxy | Nginx |
| SSL | Let's Encrypt (Free HTTPS) |
| Domain | DuckDNS (Free) |
| Container Registry | AWS ECR |

---

## 📊 Production Metrics
(Monitored via LangSmith)

| Metric | Value |
|--------|-------|
| P50 Latency | 2.18s |
| P99 Latency | 2.65s |
| Error Rate | 0% |
| Avg Tokens/Query | ~829 |
| Monthly Cost | $0.00 |

---

## ✨ Features

- Multi-Agent RAG pipeline with LangGraph (4 specialized agents)
- Hybrid semantic + keyword (BM25) search
- Indian law cross-validation (IPC, ICA 1872, Constitution, Consumer Protection Act)
- Legal suggestions engine
- PDF upload with 20MB limit enforcement
- Chat memory (k=10 sliding window)
- Session logging with performance metrics
- Rate limiting (10 req/min)
- Prompt injection detection
- Legal disclaimer on every response
- LangSmith monitoring (latency, tokens, traces)
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
LANGCHAIN_TRACING_V2=   # true or false
LANGCHAIN_PROJECT=      # enterprise-legal-counsel-ai
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
GitHub Actions (CI/CD)
├── CI: Run tests + Lint
└── CD: Build Docker → Push to AWS ECR
              ↓
         AWS ECR (Container Registry)
              ↓
         AWS EC2 t3.micro (Mumbai)
         ├── Docker Container (App)
         ├── Nginx (Reverse Proxy)
         └── Let's Encrypt (SSL)
              ↓
    https://enterprise-legal-counsel-ai.duckdns.org
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
├── static/              # React frontend (inline JSX)
├── tests/
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests with real PDFs
│   └── e2e/             # End-to-end API tests
├── api_tests/           # REST Client .http test file
├── Dockerfile
├── requirements.txt
└── .github/workflows/   # CI/CD pipelines
```

---

## 📈 Monitoring

This project uses **LangSmith** for production observability:
- Full LLM call tracing for all 4 agents
- P50/P99 latency monitoring
- Token usage and cost tracking
- Real-time error detection
- Multi-agent step visibility

---


## ⚠️ Disclaimer

This application provides AI-generated legal information for educational purposes only.
This is NOT legal advice. Always consult a qualified lawyer before taking any legal action.

---

## 👨‍💻 Developer

**Prem Kumar** | AI/ML Engineer | Hyderabad, India

- GitHub: [@prem332](https://github.com/prem332)
- Live Project: [enterprise-legal-counsel-ai.duckdns.org](https://enterprise-legal-counsel-ai.duckdns.org)