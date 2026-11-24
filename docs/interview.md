# SuryaGharSathi — Technical Interview Guide & Presentation Scripts

**Candidate:** Abhishek Dighe (ID: `SJ-64`)  
**Department:** Computer Science & Engineering (AI & ML), Sanjivani College of Engineering  
**Project:** SuryaGharSathi (सूर्याघर साथी) — AI Advisory Platform for PM Surya Ghar: Muft Bijli Yojana  
**Repository:** [github.com/abhishekdighe01/Surya_Ghar_Sathi](https://github.com/abhishekdighe01/Surya_Ghar_Sathi)  

---

## ⏱️ Elevator Pitch & Presentation Scripts

### 1. 60-Second Elevator Pitch
> *"Hello! I am Abhishek Dighe. During my AI/ML engineering work, I identified a critical problem in rooftop solar adoption under the PM Surya Ghar: Muft Bijli Yojana: homeowners struggle to calculate their exact subsidies and understand rooftop feasibility across fragmented government circulars, while commercial LLMs frequently hallucinate financial figures.  
> To solve this, I engineered **SuryaGharSathi**, an enterprise-grade AI advisory platform. It combines dense semantic retrieval using ChromaDB over official MNRE policy chunks, a deterministic subsidy calculator strictly adhering to June 2024 slabs, and an autonomous multi-step agent orchestrated with LangGraph. It features thread-safe in-memory caching for sub-millisecond query responses, automated Indian PII masking, and a 100% verified test suite. It guarantees zero financial hallucination for Indian homeowners."*

---

### 2. 3-Minute Technical Pitch
> *"Good morning panel! My name is Abhishek Dighe, and I'd like to walk you through **SuryaGharSathi**, an enterprise-grade AI advisory platform designed for Indian residential rooftop solar adoption under the Prime Minister's Surya Ghar: Muft Bijli Yojana.
> 
> **The Problem:**  
> When a typical homeowner in Maharashtra with a ₹2,000 monthly electricity bill considers rooftop solar, they face three major bottlenecks:
> 1. Ambiguity over rooftop space constraints (requiring ~10 sq m per kW).
> 2. Complex, non-linear Central Financial Assistance (CFA) subsidy slabs (₹30,000/kW up to 2 kW, ₹18,000 for the 3rd kW, capped at ₹78,000).
> 3. Standard LLMs hallucinating state-specific tariffs or inventing policy rules.
> 
> **Our Solution & Technical Architecture:**  
> We built a production system grounded in official Ministry of New and Renewable Energy (MNRE) guidelines:
> - **Hybrid Information Retrieval:** We chunked official scheme notifications with overlap preservation and indexed them in ChromaDB. When benchmarked across our 15-question test suite, our semantic RAG pipeline achieved a **66.7% Hit-Rate@3** and **100% refusal accuracy** on unanswerable queries like future MSEDCL tariff predictions.
> - **Agentic Decision Loops & HITL Safety:** In `app/graph.py`, we developed a stateful LangGraph agent with session memory. To maintain mathematical precision, the LLM is barred from calculating money directly; it delegates calculations to our deterministic `solar_cfa_calculator` tool. If a homeowner asks for a system exceeding 10 kW, the agent pauses execution and triggers a **Human-in-the-Loop (HITL) approval gate** before generating installation plans.
> - **Production Engineering & Security:** We built a FastAPI backend protected by custom **Observability Middleware** (`X-Request-ID` tracing and latency metrics), a thread-safe **TTL Query Cache** serving repeated queries in `< 1.0 ms`, and a **Security Guard** that sanitizes Indian PII (Aadhaar, PAN, phone numbers) and neutralizes prompt-injection attacks at the API perimeter.
> 
> **Impact:**  
> SuryaGharSathi is containerized with multi-stage Docker builds, backed by 35 unit/integration tests running through GitHub Actions CI/CD with zero Ruff linting violations. It transforms complex policy circulars into instant, reliable, and mathematically guaranteed financial decisions."*

---

### 3. 10-Minute Deep-Dive Presentation Outline
1. **Introduction & Context (1.5 min):** India's rooftop solar target, PM Surya Ghar Muft Bijli Yojana overview, target user persona (e.g., Kopargaon resident with 40 sq m terrace, ₹2k MSEDCL bill).
2. **System Architecture (2 min):** Explain the 4-tier design: Streamlit UI -> FastAPI Gateway & Middleware -> LangGraph Agent & Deterministic Tools -> ChromaDB Vector Store & LLM fallback.
3. **The Grounded RAG Pipeline & Benchmark (2 min):** Discuss why naive LLMs fail on domain policies; showcase the Day 8 benchmark comparing TF-IDF (Config A) vs Dense ChromaDB RAG (Config B), emphasizing Question 6 refusal.
4. **Agent State Machine & Deterministic Tools (2 min):** Walk through LangGraph nodes: `query_router`, `calculate_subsidy`, `rag_retrieval`, `approval_gate`, and `synthesize_answer`.
5. **Production Hardening, Security & Observability (1.5 min):** Explain the query cache, latency profiles, Aadhaar/PAN regex sanitization, and GitHub Actions CI/CD pipeline.
6. **Live Demo & Conclusion (1 min):** Walkthrough of the Streamlit dashboard, 10-year payback chart, and feedback capture.

---

## 🧩 Your Hardest Problem (The STAR Interview Story)

**Interview Question:** *"What was the hardest technical challenge you encountered while building SuryaGharSathi, and how did you resolve it?"*

### The STAR Narrative:
- **Situation:** While indexing official government circulars for PM Surya Ghar, we uncovered a critical temporal conflict:
  1. The **February 2024 National Portal FAQ** used older Phase-II terminology referring to *'DISCOM-discovered L1 bidding rates'* for system costs.
  2. The **June 2024 MNRE Operational Guidelines** established the newer open-market, nationwide direct vendor pricing model.
  Additionally, when asked about intermediate or fractional capacities (e.g., 2.5 kW, 3.7 kW), general LLMs repeatedly hallucinated flat multiplication rates (guessing ₹90,000 for 3 kW) instead of applying non-linear statutory subsidy slabs.
- **Task:** Eliminate financial and procedural hallucinations:
  1. Guarantee 100% mathematical precision on non-linear subsidy tier math across all fractional capacities.
  2. Resolve document conflicts between Feb-2024 and June-2024 publications so the newest official guideline always takes precedence.
- **Action:**
  1. **Deterministic Tool Pattern:** We barred the LLM from computing financial amounts. We created `solar_cfa_calculator` in `app/tools.py` which deterministically enforces MNRE June 2024 slabs (₹30,000/kW up to 2 kW, ₹18,000/kW for 2–3 kW, capped at ₹78,000). The LLM only receives and articulates the verified calculation.
  2. **Metadata Issue Dates & Recency Tie-Breaker:** In `app/chunking.py` and `app/vectorstore.py`, every chunk indexes `date_issued` as explicit metadata (`2024-02-15` vs `2024-06-25`). In ChromaDB semantic retrieval, we implemented a chronological recency tie-breaker: whenever similarity scores are close, the newest document date (`2024-06-25`) wins.
- **Result:**
  1. Financial calculation hallucination dropped to **0.0%**.
  2. Outdated *'L1 DISCOM rate'* terminology was automatically superseded by the June 2024 open-market vendor selection guidelines.
  3. Formally measured and verified across our 15-question benchmark in `eval/run_eval.py` and 35 automated Pytest unit tests.

---

## 💡 Top 10 Technical Interview Questions & Exhaustive Answers

### Q1: Why did you choose RAG over Fine-Tuning an LLM for this project?
**Answer:**
> *"We chose Retrieval-Augmented Generation (RAG) over fine-tuning for three decisive engineering reasons:
> 1. **Zero Financial Hallucination & Verifiability:** In regulatory and financial advisory, every claim must trace back to an exact legal clause. RAG enables us to inject exact source citations (e.g., *MNRE Operational Guidelines Section 4.1*), which fine-tuning cannot guarantee because weights store knowledge parametrically.
> 2. **Frequent Policy Updates:** Government circulars, benchmark prices, and Discom regulations update regularly. Updating RAG only requires updating ChromaDB chunks in seconds without costly parameter retraining.
> 3. **Guaranteed Refusal on Speculative Questions:** RAG allows strict grounding prompts. When retrieved context does not contain the answer (e.g., Question 6 regarding future MSEDCL tariff changes), the model deterministically responds: *'I cannot confirm this from the available official documents.'*"*

---

### Q2: Why is the LLM strictly prevented from calculating solar subsidies directly?
**Answer:**
> *"LLMs are autoregressive next-token predictors; they struggle with non-linear arithmetic and piecewise tier calculations. The PM Surya Ghar subsidy structure has non-linear tiers:
> - First 2 kW: ₹30,000 per kW.
> - 2 kW to 3 kW: ₹18,000 per kW.
> - Beyond 3 kW: Capped at ₹78,000 maximum.
> 
> If an LLM calculates this, it often multiplies 3 kW × ₹30,000 = ₹90,000, which is incorrect and legally misleading. We enforce the **Tool-Use Pattern**: the LLM parses user parameters and delegates the computation to our deterministic `solar_cfa_calculator` in `app/tools.py`. The LLM only receives and formats the verified output."*

---

### Q3: How did you implement and evaluate your Chunking & Embedding strategy in ChromaDB?
**Answer:**
> *"In `app/chunking.py`, we developed a metadata-preserving chunking engine:
> - We chunked 20 official records into 22 dense chunks (~150-300 words each) with 50-token overlap to maintain contextual continuity across sentences.
> - Every chunk retains rich metadata: `record_id`, `topic`, `document_title`, `issuing_body`, `date_issued`, and `source_url`.
> - In `eval/run_eval.py`, we benchmarked lexical TF-IDF against ChromaDB dense semantic embeddings across a 15-question evaluation dataset. Dense ChromaDB retrieval achieved a **66.7% Hit-Rate@3** compared to 60.0% for lexical search, showing superior performance on synonyms and semantic paraphrasing."*

---

### Q4: How does your LangGraph agent architecture work, and how does it differ from a standard ReAct loop?
**Answer:**
> *"In Day 9, we built both:
> 1. A lightweight hand-written ReAct loop in `app/agent_loop.py` using pure Python without external dependencies.
> 2. A production-grade stateful `StateGraph` in `app/graph.py` using LangGraph.
> 
> The LangGraph architecture provides significant production benefits:
> - **Explicit State Management:** Maintains a TypedDict state (`AgentState`) containing message history, system sizing, financial calculations, and approval status.
> - **Session Memory:** Uses `MemorySaver` checkpointer so conversations retain context across multi-turn interactions using a persistent `thread_id`.
> - **Deterministic Conditional Routing:** Edges route based on validated conditions rather than probabilistic LLM decisions.
> - **Human-in-the-Loop (HITL) Gate:** If system capacity exceeds 10 kW, execution pauses at the `approval_gate` node until an explicit approval flag is supplied."*

---

### Q5: How do you protect the platform against Prompt Injection and Adversarial Attacks?
**Answer:**
> *"We implemented a defense-in-depth security layer in `app/security.py`:
> 1. **Signature-based Pattern Matching:** Regex matching detects jailbreak attempts, such as 'ignore all previous instructions', 'system override', 'DAN mode', and prompt exfiltration commands ('output your system prompt').
> 2. **API Perimeter Enforcement:** The `SecurityGuard` runs prior to LLM or RAG execution in FastAPI routes (`/chat`, `/ask`, `/agent`). If an attack is detected, the request is immediately rejected with `HTTP 400 Bad Request` and a security policy violation message.
> 3. **Input Length Guards:** Enforces bounds between 2 and 1,500 characters to prevent buffer and token-flooding denial-of-service attacks."*

---

### Q6: How does the platform handle Indian Personally Identifiable Information (PII)?
**Answer:**
> *"Homeowners frequently paste electricity bills or identity documents containing sensitive data. In `app/security.py`, we implemented automatic regex-based PII redaction:
> - **Aadhaar Numbers:** 12-digit numbers formatted with or without spaces/hyphens are replaced with `[AADHAAR_REDACTED]`.
> - **PAN Cards:** 10-character alphanumeric strings (5 letters, 4 digits, 1 letter) are replaced with `[PAN_REDACTED]`.
> - **Mobile Numbers:** 10-digit numbers with optional `+91` prefix are replaced with `[PHONE_REDACTED]`.
> - **Email Addresses:** Standard email formats are replaced with `[EMAIL_REDACTED]`.
> 
> This sanitization occurs *before* any text is stored in `data/questions.json` or sent to third-party LLM providers, ensuring privacy compliance."*

---

### Q7: Explain your caching strategy and how it optimizes API latency.
**Answer:**
> *"In `app/cache.py`, we engineered `QueryCache`, a thread-safe in-memory cache utilizing Python's `threading.Lock`:
> - **Key Normalization:** Raw user queries are lowercased, stripped of punctuation, and collapsed of excess whitespace before generating a deterministic MD5 hash key. This ensures `'How much subsidy for 3 kW?'` and `'how much subsidy for 3 kw'` hit the identical cache entry.
> - **Time-To-Live (TTL):** Configured with a 1-hour TTL (3,600 seconds), with automatic timestamp-based eviction.
> - **Latency Benefit:** A cache hit responds in `< 1.0 ms`, bypassing ChromaDB retrieval (~100 ms) and LLM token generation (~1,000 ms), delivering over **99% latency reduction** on common inquiries and saving API token quotas."*

---

### Q8: How did you implement Observability and Request Tracing?
**Answer:**
> *"We implemented an `ObservabilityMiddleware` using Starlette's `BaseHTTPMiddleware` in `app/middleware.py`:
> - **Distributed Correlation ID:** Injects or propagates an `X-Request-ID` UUID header across every incoming and outgoing HTTP transaction.
> - **High-Precision Timing:** Uses `time.perf_counter()` to measure total request duration in milliseconds and injects `X-Process-Time-Ms` in response headers.
> - **Structured Logging:** Emits standardized log entries capturing correlation ID, HTTP method, path, response status code, and latency in milliseconds for log aggregation tools."*

---

### Q9: How is your testing strategy and CI/CD pipeline architected?
**Answer:**
> *"Our testing and CI/CD architecture is built on automated, multi-tiered verification:
> - **Unit & Integration Testing:** 35 automated tests in `tests/` covering dataclass models, the deterministic solar calculator, TF-IDF search, ChromaDB vector queries, RAG grounded responses, FastAPI endpoints, thread-safe caching, and security sanitization.
> - **Linting & Code Quality:** Enforced via `pyproject.toml` with `ruff check .` maintaining 0 errors and standardized Python 3.10+ conventions.
> - **CI Automation:** A GitHub Actions workflow in `.github/workflows/ci.yml` triggers on every push and pull request to `main`, installing dependencies, executing Ruff, running Pytest, and verifying Docker container builds."*

---

### Q10: How does SuryaGharSathi specifically cater to the homeowner in Kopargaon, Maharashtra?
**Answer:**
> *"Our reference persona is a homeowner in Kopargaon, Ahmednagar district, with a ₹2,000 monthly MSEDCL electricity bill and a 40 sq m concrete terrace:
> - **System Sizing:** 2 kW to 3 kW is optimal. A 3 kW plant generates ~360 units/month, eliminating a ₹2,000 electricity bill.
> - **Terrace Feasibility:** A 3 kW installation requires ~30 sq m of shadow-free rooftop space. With 40 sq m available, the rooftop is feasible with 10 sq m of spare space.
> - **Financial Breakdown:**
>   - Gross Project Cost: ~₹1,50,000 (at ~₹50,000/kW benchmark).
>   - PM Surya Ghar CFA Subsidy: **₹78,000** (₹60,000 for first 2 kW + ₹18,000 for 3rd kW).
>   - Net Outlay for Homeowner: **₹72,000**.
>   - Monthly Savings: ~₹1,800 to ₹2,000.
>   - Estimated Simple Payback: **~3.3 years**, followed by over 20 years of free clean solar electricity under the 25-year panel warranty."*
