# SuryaGharSathi (सूर्याघर साथी) ☀️⚡

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

## 🚀 How to Run (Day 1)

### 1. Prerequisites
- Python 3.10+ installed on your system.
- PowerShell or Terminal.

### 2. Setup Virtual Environment (Recommended)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Run the Introduction Script
```powershell
python day01_intro.py
```

### 4. Run the Interactive Menu
```powershell
python day01_menu.py
```

---

## ⚠️ Important Disclaimer
*All scheme rules, subsidy slabs, and procedures are retrieved from official Ministry of New and Renewable Energy (MNRE) publications. Financial estimates, savings, and payback figures are approximate calculations provided for educational evaluation and do not represent contractual financial advice. Always verify with MSEDCL and the PM Surya Ghar National Portal before making final commercial vendor commitments.*
