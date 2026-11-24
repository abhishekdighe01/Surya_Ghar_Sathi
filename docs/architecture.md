# SuryaGharSathi (सूर्याघर साथी) — System Architecture Blueprint

**Candidate:** Abhishek Dighe (ID: `SJ-64`)  
**Department:** Computer Science & Engineering (AI & ML), Sanjivani College of Engineering  
**Version:** 1.0.0 (Production Release)  
**Target Policy:** PM Surya Ghar: Muft Bijli Yojana (MNRE Guidelines June 2024)  

---

## 1. High-Level System Architecture

The SuryaGharSathi platform follows a modern, decoupled microservices architecture comprising five core layers:
1. **Presentation Layer:** Interactive Streamlit web interface for homeowners.
2. **API & Gateway Layer:** FastAPI REST backend fortified with Observability Middleware, Thread-Safe In-Memory Query Caching, and Security Guardrails.
3. **Agentic Orchestration Layer:** LangGraph state machine with memory and Human-in-the-Loop approval gates.
4. **Deterministic Tool Layer:** Exact MNRE calculation engines ensuring zero financial hallucination.
5. **Knowledge & Retrieval Layer:** ChromaDB vector database with dense embeddings and Scikit-Learn TF-IDF search.

```mermaid
graph TD
    subgraph Client ["Client Layer"]
        User["Indian Homeowner (e.g., Kopargaon)"] --> UI["Streamlit UI (Port 8501)"]
    end

    subgraph API_Gateway ["FastAPI Gateway & Security Layer (Port 8000)"]
        UI -->|HTTP POST /ask, /agent| MW["Observability Middleware (X-Request-ID, X-Process-Time-Ms)"]
        MW --> SEC["Security Guard (Prompt Injection Defense & PII Redaction)"]
        SEC --> CACHE{"TTL Query Cache (<1ms)"}
    end

    subgraph Agent_Layer ["Agent & Execution Layer"]
        CACHE -->|Cache Miss| LG["LangGraph Stateful Agent (app/graph.py)"]
        LG --> ROUTER{"Intent Router"}
    end

    subgraph Tools_Storage ["Deterministic Tools & Storage Layer"]
        ROUTER -->|Subsidy & Sizing| CALC["Deterministic Calculator (solar_cfa_calculator)"]
        ROUTER -->|Scheme Regulations| VSTORE["ChromaDB Vector Store (22 Indexed Chunks)"]
        ROUTER -->|General Advisory| LLM["LLM Engine (Gemini 2.5 Flash / Groq LLaMA 3.3)"]
        LG -->|System > 10 kW| GATE["HITL Safety Approval Gate"]
    end

    CACHE -->|Cache Hit| UI
    CALC --> LG
    VSTORE --> LG
    LLM --> LG
    LG --> UI
```

---

## 2. End-to-End Request & Data Flow (Sequence Diagram)

The following sequence illustrates a homeowner inquiring about a 3 kW solar system with a ₹2,000 monthly bill and 40 sq m rooftop terrace.

```mermaid
sequenceDiagram
    autonumber
    actor Homeowner as Homeowner (Abhishek Dighe)
    participant UI as Streamlit Web UI
    participant Middleware as Observability Middleware
    participant Security as Security Guard
    participant Cache as Query Cache
    participant LangGraph as LangGraph Agent
    participant Calc as Solar Calculator
    participant ChromaDB as ChromaDB Vector Store
    participant LLM as LLM Engine

    Homeowner->>UI: Enters query: "3 kW solar for my 40 sq m roof in Kopargaon"
    UI->>Middleware: POST /agent (monthly_bill=2000, terrace_sqm=40)
    Middleware->>Security: Validate & sanitize input
    Security->>Security: Mask Aadhaar/PAN/Phone & check jailbreaks
    Security->>Cache: Check cached normalized query
    alt Cache Hit (< 1 ms)
        Cache-->>UI: Return instant cached response
    else Cache Miss
        Cache->>LangGraph: Invoke StateGraph with AgentState
        LangGraph->>Calc: Compute CFA subsidy, net cost & payback
        Calc-->>LangGraph: Subsidy=₹78,000, Net=₹72,000, Payback=3.3 yrs
        LangGraph->>ChromaDB: Query dense chunks for rooftop requirements
        ChromaDB-->>LangGraph: Returns Record #16 (10 sq m/kW rule)
        LangGraph->>LLM: Synthesize final grounded advisory with citations
        LLM-->>LangGraph: Formatted response with exact MNRE citations
        LangGraph->>Cache: Save synthesized response with 1-hr TTL
        LangGraph-->>Middleware: Return AgentResponse
        Middleware-->>UI: Ingest response with X-Process-Time-Ms header
    end
    UI-->>Homeowner: Display subsidy breakdown, 10-yr chart & citations
```

---

## 3. LangGraph State Machine & Human-in-the-Loop Safety Gate

To guarantee safety, commercial-scale solar proposals (>10 kW) are gated behind an approval state:

```mermaid
stateDiagram-v2
    [*] --> QueryRouter: User Question Received
    
    QueryRouter --> CalculateSubsidy: Calculation Needed
    QueryRouter --> RAGRetrieval: Scheme Knowledge Needed
    QueryRouter --> SynthesizeAnswer: General Query
    
    CalculateSubsidy --> CheckCapacity: Sizing Computed
    
    state CheckCapacity <<choice>>
    CheckCapacity --> ApprovalGate: Capacity > 10 kW
    CheckCapacity --> SynthesizeAnswer: Capacity <= 10 kW
    
    ApprovalGate --> AwaitingApproval: approved == False
    AwaitingApproval --> SynthesizeAnswer: approved == True
    
    RAGRetrieval --> SynthesizeAnswer: Chunks Retrieved
    SynthesizeAnswer --> [*]: Return Grounded JSON
```

---

## 4. Key Subsystem Specifications

### 4.1 Ingestion & Chunking Subsystem (`app/chunking.py`, `app/embed.py`)
- **Document Source:** Official MNRE PM Surya Ghar Operational Guidelines (June 2024) and National Portal FAQ repository.
- **Chunk Size:** 150 - 300 words per chunk.
- **Overlap:** 50 tokens with boundary preservation to eliminate information loss across chunk boundaries.
- **Metadata Fields:** `record_id`, `topic`, `document_title`, `issuing_body`, `date_issued`, `source_url`.
- **Vector Store:** ChromaDB with dense Euclidean/Cosine similarity indexing.

### 4.2 Deterministic Solar Calculator (`app/tools.py`)
- Strictly enforces Central Financial Assistance (CFA) subsidy policy:
  - First 2 kW: ₹30,000 / kW
  - 2 kW to 3 kW: ₹18,000 / kW
  - Max Subsidy Cap: ₹78,000 (for $\ge 3$ kW)
- Rooftop Feasibility: $\approx 10\text{ m}^2$ (100–110 sq ft) per 1 kW.
- Generation Estimate: $\approx 120\text{ units/kW/month}$ in Maharashtra.
- Payback Computation: Net investment divided by annual MSEDCL electricity bill savings.

### 4.3 Caching & Performance Subsystem (`app/cache.py`)
- Thread-safe implementation using `threading.Lock`.
- Deterministic key hashing using MD5 of normalized lowercase query text.
- 1-hour configurable Time-To-Live (TTL) with active and passive expiration.
- Reduces repetitive query latency from $\sim 1,200\text{ ms}$ down to $< 1.0\text{ ms}$.

### 4.4 Security & Data Privacy Subsystem (`app/security.py`)
- Regular expression sanitization engine for Indian PII:
  - Aadhaar: `\b([2-9]\d{3}[-\s]?\d{4}[-\s]?\d{4})\b` -> `[AADHAAR_REDACTED]`
  - PAN: `\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b` -> `[PAN_REDACTED]`
  - Mobile: `(\+91[\-\s]?)?([6-9]\d{9})\b` -> `[PHONE_REDACTED]`
- Pattern matching defense against Prompt Injection and adversarial jailbreaks.

---

## 5. Viva Voce Quick Reference

| Viva Question | Concise Engineering Response |
|---|---|
| **What is the core innovation of SuryaGharSathi?** | Unifying deterministic financial calculation tools with grounded RAG semantic retrieval and LangGraph agentic decision loops to eliminate hallucinations in public policy advisory. |
| **Why not let the LLM calculate the subsidy?** | LLMs are non-deterministic token predictors that frequently fail on tiered arithmetic. Subsidies are governed by strict statutory rules requiring 100% mathematical precision. |
| **How did you prevent hallucinations on future tariffs?** | Using grounded system prompts and evaluation checks. When official documents do not contain future tariff forecasts (Question 6), the RAG pipeline strictly refuses to answer. |
| **How is the system deployed?** | Multi-container Docker Compose setup orchestrated with non-root Linux users, health checks, and a full GitHub Actions CI/CD pipeline enforcing 35 Pytest tests and Ruff linting. |
