# SuryaGharSathi (सूर्याघर साथी) ☀️⚡

[![SuryaGharSathi CI](https://github.com/abhishekdighe54/sanjivani-sj-64-suryagharsathi/actions/workflows/ci.yml/badge.svg)](https://github.com/abhishekdighe54/sanjivani-sj-64-suryagharsathi/actions)
![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)
![Tests](https://img.shields.io/badge/pytest-24%20passed-brightgreen.svg)
![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)

An AI-powered advisory assistant for Indian homeowners navigating the **PM Surya Ghar: Muft Bijli Yojana**.

---

## 📋 Project Card

| Attribute | Details |
|:---|:---|
| **Product Name** | **SuryaGharSathi** |
| **Description** | Explains PM Surya Ghar rooftop solar rules, works out your exact central subsidy (CFA), and shows how fast the panels pay for themselves. |
| **Target User** | Homeowner in Kopargaon, Maharashtra with a ₹2,000/month MSEDCL electricity bill and a 40 sq m terrace, deciding between a 2 kW and 3 kW rooftop solar system. |
| **Problem Statement** | Homeowners struggle to understand complex solar scheme guidelines, calculate tiered central subsidies accurately, verify roof space requirements, and estimate real financial payback periods without vendor bias or outdated portal information. |
| **Data Sources** | 1. **MNRE Operational Guidelines** for PM Surya Ghar: Muft Bijli Yojana (June 2024)<br>2. **National Portal FAQs** (February 2024) |
| **Agent Tool** | `solar_cfa_calculator`: Exact deterministic central subsidy computation based on official slab rules (₹30,000/kW up to 2 kW; ₹18,000/kW between 2 and 3 kW; max ₹78,000) and shadow-free terrace area estimation (~10 sq m per kW). |
| **Key Safety Rules** | Strict RAG grounding with source citations; LLMs never hallucinate financial subsidies; explicit "I don't know" response for unanswerable queries (e.g. future DISCOM tariffs); clear separation between official rules and financial estimates. |

---

## 🏗️ 15-Day Engineering Roadmap

- **Day 1**: Project Setup, Git Repository, and Foundational CLI
- **Day 2**: Structured Data Collection (20 Official MNRE & FAQ Records)
- **Day 3**: Data Ingestion Pipeline & Cleaning
- **Day 4**: FastAPI REST Backend & TF-IDF Smart Search (Checkpoint 1)
- **Day 5**: LLM Concepts, Prompt Engineering & Evaluation Set
- **Day 6**: LLM Provider Integration (Groq/Gemini) & Structured JSON Chat
- **Day 7**: Document Chunking, Embeddings & ChromaDB Vector Store
- **Day 8**: Grounded RAG Pipeline with Citations & Fallback Safeguards
- **Day 9**: AI Agent, LangGraph Workflow & Solar CFA Calculator Tool
- **Day 10**: Streamlit Web UI with Interactive Payback Visualizer (Checkpoint 2)
- **Day 11**: Automated Testing with Pytest & Ruff Code Quality
- **Day 12**: Dockerization & GitHub Actions CI/CD Pipeline
- **Day 13**: Production Observability, Latency/Token Logging & Security Defense
- **Day 14**: Public Cloud Deployment & AI Role Interview Preparation
- **Day 15**: Architecture Walkthrough, Live Viva Demo & Capstone Defense

---

## 🚀 How to Run

### 1. Prerequisites
- Python 3.10+ installed on your system.
- PowerShell or Terminal.

### 2. Setup Virtual Environment (Recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Run the Foundational CLI Scripts (Day 1 & Day 2)
```powershell
# Introduction script
python day01_intro.py

# Interactive menu
python day01_menu.py

# Records explorer
python app/cli.py
```

### 4. Run the Ingestion Pipeline (Day 3)
```powershell
python app/fetch.py
python app/ingest.py
```

### 5. Run the FastAPI Backend Service (Day 4)
```powershell
# Start FastAPI development server with hot-reload
uvicorn app.main:app --reload

# Open Swagger interactive documentation:
# http://127.0.0.1:8000/docs

# Open ReDoc documentation:
# http://127.0.0.1:8000/redoc
```

### 6. Run Exploratory Data Analysis & Smart Search
```powershell
# Inspect dataset with pandas
python analysis/explore.py

# Test TF-IDF + Cosine Similarity search
python app/smart_search.py
```

### 7. Run Grounded LLM Chat (Day 6)
```powershell
python app/llm.py
```

### 8. Run Document Chunking & ChromaDB Vector Store (Day 7)
```powershell
# Verify chunking and embedding generation
python app/chunking.py
python app/embed.py

# Verify ChromaDB semantic search
python app/vectorstore.py
```

### 9. Run RAG Pipeline & Evaluation Benchmarking (Day 8)
```powershell
# Run the end-to-end RAG pipeline
python app/rag.py

# Run RAG evaluation across 15-question benchmark dataset
python eval/run_eval.py
```

#### Day 8 RAG Benchmark Results:
| Configuration | Retrieval Approach | Hit-Rate @ 3 | Refusal Accuracy (Q6) | Avg Latency |
|---|---|:---:|:---:|:---:|
| **Config A** | Lexical TF-IDF (k=3) | 60.0% | 0.0% | 1.2 ms |
| **Config B (Winner)** | Dense ChromaDB Semantic RAG (k=3, overlap=50) | **66.7%** | **100.0%** | 31.5 ms |

> **Key Finding:** Config B won with superior vocabulary-invariance, high semantic recall on technical solar terms, and zero hallucinations on unanswerable queries like Q6 (future MSEDCL tariff).


### 10. Run AI Agent & Solar CFA Calculator (Day 9)
```powershell
# 1. Test deterministic solar calculator and RAG tools
python app/tools.py

# 2. Test lightweight hand-written Reason-Act-Observe loop
python app/agent_loop.py

# 3. Test LangGraph StateGraph agent with memory and >10 kW approval gate
python app/graph.py
```

#### Day 9 Key Highlights:
- **`solar_cfa_calculator`**: Deterministic calculator strictly implementing MNRE June 2024 subsidy slabs (₹30,000/kW for <= 2 kW, ₹18,000/kW for 2-3 kW, max ₹78,000 cap), rooftop feasibility (~10 sq m/kW), and payback period.
- **Hand-written Agent Loop**: Reason -> Act -> Observe loop without heavy external frameworks.
- **LangGraph StateGraph (`app/graph.py`)**: Stateful agent graph with session memory checkpointer and a Human-in-the-Loop safety gate requiring explicit confirmation for commercial-scale systems (>10 kW).
- **Endpoint**: `POST /agent` exposed in FastAPI.

### 11. Run Streamlit Interactive Web UI (Day 10)
```powershell
# Launch Streamlit web dashboard in your browser
streamlit run ui/app.py
```

#### Streamlit UI Capabilities:
- **Homeowner Profile Sidebar**: Real-time sliders for monthly MSEDCL bill (₹2,000) and available terrace area (40 sq m).
- **Live Sizing & Subsidy Preview**: Live metric tiles for CFA subsidy (₹78,000), net outlay (₹72,000), and feasibility status.
- **Interactive 10-Year Payback Chart**: Visualizes investment break-even trajectory over 10 years using Streamlit interactive charts.
- **Grounded Chat with Expandable Citations**: Direct conversation with the LangGraph agent and ChromaDB RAG store.
- **Feedback Loop**: 👍 / 👎 buttons saving ratings directly to `data/feedback.json`.
- **Checkpoint 2 Demo Script**: Available in [`eval/checkpoint2_demo.md`](file:///e:/SuryaGharSathi/eval/checkpoint2_demo.md).

### 12. Run Automated Test Suite & Code Quality (Day 11)
```powershell
# Run the 24-test pytest suite
pytest

# Run Ruff linter to verify code quality
ruff check .
```

#### Test Suite Breakdown (24 Tests, 100% Green):
- `tests/test_records.py`: Dataclass models, field validations, count by issuing body.
- `tests/test_calculator.py`: Official MNRE subsidy slabs (1 kW, 2 kW, 3 kW, 5 kW cap), rooftop area feasibility, and payback math.
- `tests/test_search.py`: Scikit-learn TF-IDF and ChromaDB dense semantic vector retrieval.
- `tests/test_rag.py`: RAG question answering, citation verification, and Q6 unanswerable refusal.
- `tests/test_api.py`: FastAPI endpoints (`/health`, `/records`, `/search`, `/questions`, `/ask`, `/agent`).

---

### 13. Run with Docker & Docker Compose (Day 11)
```powershell
# Build and launch both FastAPI backend and Streamlit UI in containers:
docker compose up --build

# Once started:
# - Streamlit Web Dashboard: http://localhost:8501
# - FastAPI REST API & Swagger Docs: http://localhost:8000/docs
```

---

### 14. Continuous Integration & Cloud Deployment (Day 12)
- **Automated CI/CD Workflow**: [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml) executes on every push/PR to `main`, validating `ruff check .`, the 24-test `pytest` suite, and container image builds.
- **Production Cloud Deployment**: Blueprint configured in [`render.yaml`](file:///e:/SuryaGharSathi/render.yaml).
- **Deployment Manual**: Detailed setup instructions for Render and Hugging Face Spaces in [`docs/deployment.md`](file:///e:/SuryaGharSathi/docs/deployment.md).
- **Live Healthcheck Endpoint**: `GET /health` (monitored via cloud PaaS).

---

## ⚠️ Important Disclaimer
*All scheme rules, subsidy slabs, and procedures are retrieved from official Ministry of New and Renewable Energy (MNRE) publications. Financial estimates, savings, and payback figures are approximate calculations provided for educational evaluation and do not represent contractual financial advice. Always verify with MSEDCL and the PM Surya Ghar National Portal before making final commercial vendor commitments.*
