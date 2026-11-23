# SuryaGharSathi — Checkpoint 2 Live RAG & Agent Demo Guide

**Project:** SuryaGharSathi (सूर्याघर साथी)  
**Student:** Abhishek Dighe (ID: `SJ-64`, CSE AI & ML, Sanjivani)  
**Target User Persona:** Homeowner in Kopargaon, Maharashtra (Monthly Bill: ₹2,000, Terrace: 40 sq m, System: 2 kW vs 3 kW)  
**Milestone:** Checkpoint 2 (Days 6–10: LLMs, Prompts, Embeddings, ChromaDB RAG, LangGraph Agent, Streamlit UI)

---

## ⏱️ 4-Minute Live Demo Script & Walkthrough

### 1. Introduction (0:00 – 0:30)
> *"Good morning respected panelists. My name is Abhishek Dighe, and I am presenting **SuryaGharSathi (सूर्याघर साथी)**, an AI-powered advisory agent for the PM Surya Ghar: Muft Bijli Yojana.*
> *Our target persona is a homeowner in Kopargaon, Maharashtra with a ₹2,000 monthly MSEDCL electricity bill and a 40 square metre shadow-free terrace. Our system combines dense semantic vector retrieval in ChromaDB with deterministic Python tools and a stateful LangGraph agent."*

---

### 2. Demo Query 1: Solar Sizing, Subsidy & Payback (0:30 – 1:30)
- **Question Asked:**
  > *"Can I install a 3 kW solar plant on my 40 sq m roof in Kopargaon with a ₹2,000 electricity bill, and what will be my net cost and payback?"*
- **Live Output to Point to on Screen:**
  1. **Central Subsidy (CFA):** Exactly **₹78,000** (₹60,000 for the first 2 kW + ₹18,000 for the 3rd kW).
  2. **Net Outlay:** Gross benchmark cost ₹1,50,000 minus ₹78,000 subsidy = **₹72,000**.
  3. **Rooftop Feasibility:** 3 kW requires **30 sq m** ($\sim 10\text{ sq m/kW}$). With 40 sq m available, the agent flags **Feasible ✅ with a 10 sq m safety margin**.
  4. **Payback:** Monthly generation of $\sim 360\text{ kWh}$ completely offsets the ₹2,000 bill, giving an estimated **3.0-year payback period**.
  5. **Streamlit Chart:** Point to the interactive 10-year economics chart showing cumulative savings (green line) intersecting the capital outlay (red line) at Year 3.

---

### 3. Demo Query 2: Technical Warranties & Scheme Rules (1:30 – 2:30)
- **Question Asked:**
  > *"What are the mandatory warranty periods on solar panels and inverters under the scheme?"*
- **Live Output to Point to on Screen:**
  1. **Grounding:** Shows 25-year panel performance warranty and minimum 5-year inverter/system maintenance warranty.
  2. **Verifiable Citations:** Expand the citation dropdown:
     - *Operational Guidelines for Implementation of PM Surya Ghar: Muft Bijli Yojana (June 2024), Clause 8*
     - *National Portal FAQs (February 2024)*

---

### 4. Demo Query 3: Out-of-Scope / Unanswerable Tariff Query (2:30 – 3:15)
- **Question Asked:**
  > *"What will MSEDCL's electricity tariff per unit be next year?"*
- **Live Output to Point to on Screen:**
  - **Refusal Safeguard:** The agent strictly returns:
    > *"I cannot confirm this from the available official documents. Electricity tariffs for MSEDCL are determined annually by the Maharashtra Electricity Regulatory Commission (MERC) and are not established in PM Surya Ghar scheme guidelines."*
  - **Explain to Panel:** Explain that vanilla LLMs hallucinate a predicted price. SuryaGharSathi enforces a similarity threshold and keyword safeguard to maintain 100% factual integrity.

---

### 5. Technical Failure Fixed (3:15 – 4:00)
> *"When building this system, our biggest failure mode was **LLM arithmetic hallucination**. When asked for subsidies on non-integer or multi-slab systems (like 2.5 kW or 3 kW), language models either applied obsolete Phase-II guidelines or miscalculated the staggered formula.*
> 
> *We resolved this with a dual-engine architecture:
> 1. We built a deterministic Python tool (`solar_cfa_calculator` in `app/tools.py`) that strictly enforces the June 2024 MNRE slabs.
> 2. We wired it into a **LangGraph StateGraph** that dynamically routes arithmetic queries to the Python tool and policy queries to ChromaDB, with an approval gate for commercial systems exceeding 10 kW.*
> *This achieved **100% mathematical accuracy** and **66.7% semantic hit-rate@3** across our 15-question benchmark."*

---

## 🏛️ Checkpoint 2 Architecture Reference

```
                             [ Streamlit Web UI (ui/app.py) ]
                                            │
                                  HTTP REST / Direct
                                            ▼
                           [ FastAPI Service (app/main.py) ]
                                            │
                                            ▼
                         [ LangGraph Agent (app/graph.py) ]
                            ├── MemorySaver (Thread ID)
                            └── Safety Gate (>10 kW Approval)
                                   │               │
                 ┌─────────────────┴─┐           ┌─┴─────────────────┐
                 ▼                   ▼           ▼                   ▼
     [ solar_cfa_calculator ]  [ Net Metering ]  [ rag_search_tool ] [ ChromaDB Store ]
        (app/tools.py)         (app/tools.py)    (app/rag.py)       (app/vectorstore.py)
```
