# SuryaGharSathi — Portfolio Resume Guide & Technical Bullets

**Developer:** Abhishek Dighe (Student ID: `SJ-64`)  
**Department:** Computer Science & Engineering (AI & ML), Sanjivani College of Engineering  
**Project Repository:** [github.com/abhishekdighe01/Surya_Ghar_Sathi](https://github.com/abhishekdighe01/Surya_Ghar_Sathi)  
**Specialization:** Generative AI, RAG Systems, Multi-Agent Orchestration, Production AI Engineering  

---

## 📄 Quantifiable Resume Project Bullets (STAR Format)

### 🔹 Bullet 1: Grounded RAG & Vector Retrieval Engine
> **Architected an enterprise-grade Retrieval-Augmented Generation (RAG) system for PM Surya Ghar solar policy advisory**, utilizing **ChromaDB** dense vector indexing and hybrid TF-IDF retrieval across 22 official MNRE policy chunks; achieved **66.7% Hit-Rate@3** on technical domain queries and **100% refusal accuracy** on ungrounded out-of-scope queries, reducing hallucination rates to zero on non-verified tariff claims.

### 🔹 Bullet 2: Multi-Agent Orchestration & Stateful Human-in-the-Loop Workflow
> **Engineered an autonomous multi-step advisory agent using LangGraph and a hand-written ReAct loop**, orchestrating deterministic calculation tools (`solar_cfa_calculator`) with semantic knowledge retrieval; implemented session memory checkpointing and an **automated Human-in-the-Loop (HITL) safety approval gate** for commercial-scale rooftop solar requests (>10 kW) to guarantee strict regulatory compliance.

### 🔹 Bullet 3: Production Microservice, Sub-Millisecond Caching & Security Guardrails
> **Engineered and deployed a production-grade FastAPI microservice and Streamlit UI in multi-container Docker architecture**, integrating custom **Observability Middleware (`X-Request-ID`, `X-Process-Time-Ms`)**, an in-memory **thread-safe TTL query cache (<1 ms latency for cache hits)**, regex-based **Indian PII sanitization (Aadhaar, PAN, phone numbers)**, and adversarial prompt-injection defenses; established 100% CI/CD automation via **GitHub Actions** with **35 automated Pytest unit tests** and **Ruff linting**.

---

## 🛠️ Technical Skills Demonstrated

| Dimension | Technologies & Methodologies |
|---|---|
| **Large Language Models & Frameworks** | Google Gemini 2.5 Flash, Groq LLaMA-3.3-70B, LangGraph, LangChain Core, ReAct Loops |
| **Information Retrieval & RAG** | ChromaDB, Cosine Similarity, Dense Embeddings, TF-IDF (Scikit-Learn), Semantic Chunking |
| **Backend & Microservices** | FastAPI, Starlette Middleware, Pydantic v2, Python 3.10+, RESTful API Design |
| **Performance & Security** | Thread-safe in-memory TTL caching, Sub-millisecond retrieval, Indian PII Masking (Aadhaar/PAN), Jailbreak & Injection Defense |
| **Frontend & UI** | Streamlit, Dynamic 10-Year Payback Visualization, Interactive Sliders, User Feedback Loop |
| **DevOps & Testing** | Docker, Docker Compose, GitHub Actions CI/CD, Pytest (35 unit/integration tests), Ruff (0 errors), Render Cloud IaC |

---

## 🎯 Target Persona & Real-World Impact

- **Target Persona:** Residential homeowner in Kopargaon, Ahmednagar, Maharashtra with a monthly electricity bill of ~₹2,000 (MSEDCL tariff slab) and 40 sq m rooftop terrace.
- **Problem Solved:** Resolves homeowner confusion regarding rooftop area feasibility (10 sq m/kW rule), exact MNRE Central Financial Assistance subsidy calculation (₹78,000 for 3 kW system), and estimated financial payback (~3.3 years).
- **Zero Hallucination Guarantee:** The system strictly refuses unanswerable speculative questions (such as future MSEDCL tariff changes) with: *"I cannot confirm this from the available official documents."*
