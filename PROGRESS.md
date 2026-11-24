# SuryaGharSathi — 15-Day AI Project Development Progress Tracker

| Day | Date / Session | Objective | Status | Commit / Notes |
|:---:|:---|:---|:---:|:---|
| **Day 1** | Project Setup & GitHub Repository | Setup environment, project card, `day01_intro.py`, `day01_menu.py`, Git repo | **COMPLETED** | Commit `50635a3` |
| **Day 2** | Structured Data Collection | 20 real records (MNRE Guidelines + FAQ), dataclass models, records CLI | **COMPLETED** | Commit `e618a32` & Day 2 CLI validated |
| **Day 3** | Data Ingestion Pipeline | Ingest real data, clean text, handle errors, save `data/records.json` | **COMPLETED** | Ingestion pipeline & `records.json` verified |
| **Day 4** | FastAPI Backend & Smart Search | REST API (`/health`, `/records`, `/search`), TF-IDF + Cosine search | **COMPLETED** | FastAPI endpoints & TF-IDF validated (tag: `week-1`) |
| **Day 5** | LLM Fundamentals & Checkpoint 1 | LLM guide, 10 eval questions (incl. Q6 unknown), Checkpoint 1 review | **COMPLETED** | Eval set, prompt comparison & Checkpoint 1 complete (tag: `checkpoint-1`) |
| **Day 6** | LLM Integration & Prompt Engineering | Groq/Gemini LLM wrapper, system prompt, `POST /chat`, structured JSON | **COMPLETED** | LLM wrapper, prompts & `POST /chat` endpoint verified |
| **Day 7** | Document Chunking & Embeddings | Metadata-preserving chunking, embeddings, ChromaDB vector store | **COMPLETED** | Persistent Chroma collection, chunking, embeddings & `/search/semantic` verified |
| **Day 8** | RAG Implementation & Evaluation | Retrieve + Augment + Generate, citations, "I don't know" safeguard, 15-row eval | **COMPLETED** | RAG pipeline, `POST /ask`, eval benchmark Config B winner (66.7% hit-rate@3, 100% refusal) |
| **Day 9** | AI Agent & Solar CFA Calculator Tool | Tool calling, deterministic `solar_cfa_calculator`, LangGraph workflow | **COMPLETED** | `app/tools.py`, `app/agent_loop.py`, `app/graph.py`, `POST /agent` (memory + >10kW approval) |
| **Day 10** | Streamlit UI & Checkpoint 2 | Chat UI, payback chart, citations, feedback, Checkpoint 2 live demo | **COMPLETED** | `ui/app.py`, `eval/checkpoint2_demo.md`, feedback collector, tag `checkpoint-2` |
| **Day 11** | Testing, Quality & Dockerization | Pytest test suite (24 tests green), Ruff clean (0 errors), Dockerfile & docker-compose | **COMPLETED** | `tests/`, `pyproject.toml`, `Dockerfile`, `docker-compose.yml`, `.dockerignore` |
| **Day 12** | CI/CD with GitHub Actions & Deployment | GitHub Actions CI workflow, PR review flow, public deployment configs | **COMPLETED** | `.github/workflows/ci.yml`, `render.yaml`, `docs/deployment.md`, CI status badge |
| **Day 13** | Production Hardening & Observability | Latency/token tracking, cache, prompt injection defense, safety disclaimers | **COMPLETED** | `app/middleware.py`, `app/cache.py`, `app/security.py`, 35 tests green, `docs/resume.md` |
| **Day 14** | Public Deployment & Interview Prep | Render/Hugging Face deployment, public URL testing, `interview.md` | **NOT STARTED** | — |
| **Day 15** | Architecture & Final Demo | Architecture diagram, viva prep, final tag, 5-minute presentation | **NOT STARTED** | Checkpoint 3 / Final Demo |

---

## Daily Log

### Day 1: Project Setup and GitHub Repository
- **Status:** IN PROGRESS
- **Tasks Completed:**
  - Workspace inspection and PDF requirements extraction verified.
  - Project tracker and architecture blueprint established.
- **Files Created / Modified:**
  - `PROGRESS.md`
- **Current Goal:**
  - Create `README.md`, `day01_intro.py`, `day01_menu.py`, `requirements.txt`, `.gitignore`.
  - Initialize git repository and test interactive CLI scripts.
