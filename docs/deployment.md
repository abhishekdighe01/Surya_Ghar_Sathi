# SuryaGharSathi — Production Cloud Deployment Guide

**Project:** SuryaGharSathi (सूर्याघर साथी)  
**Author:** Abhishek Dighe (ID: `SJ-64`, CSE AI & ML, Sanjivani)  
**Target Milestone:** Day 12 (Continuous Integration & Public Cloud Deployment)

---

## 🌐 1. Deployment Overview

In modern AI engineering, applications are packaged as Docker containers and deployed to cloud Platform-as-a-Service (PaaS) providers for zero-maintenance hosting, automated TLS certificates, and continuous deployment (CD).

| Component | Cloud Host | Port | Health Endpoint |
|---|---|:---:|:---:|
| **FastAPI Backend Service** | Render / Railway / Hugging Face Spaces | `8000` | `/health` |
| **Streamlit Interactive UI** | Streamlit Community Cloud / Render | `8501` | `/` |

---

## 🚀 2. Option A: One-Click Deployment via Render (Recommended)

Render provides native Docker support and reads our [render.yaml](file:///e:/SuryaGharSathi/render.yaml) blueprint automatically.

### Step-by-Step Instructions:

1. **Sign Up & Connect GitHub:**
   - Go to [https://dashboard.render.com](https://dashboard.render.com) and sign in using your GitHub account (`abhishekdighe54`).
2. **Create New Blueprint:**
   - Click **"New +"** in the top navigation bar.
   - Select **"Blueprint"**.
3. **Select Your Repository:**
   - Choose `sanjivani-sj-64-suryagharsathi`.
   - Render automatically detects `render.yaml` in the repository root.
4. **Configure Environment Secrets:**
   - Under Environment Variables, supply your live Gemini API Key:
     - `GEMINI_API_KEY`: `your_actual_gemini_api_key`
     - `LLM_PROVIDER`: `gemini`
5. **Click "Apply":**
   - Render will build the Docker image, run health checks against `/health`, and assign a public URL:
     ```text
     https://suryagharsathi-api.onrender.com
     ```
6. **Verify Health Endpoint:**
   ```powershell
   curl https://suryagharsathi-api.onrender.com/health
   # Expected response: {"status":"ok","app":"SuryaGharSathi","version":"1.0.0","records_count":20,...}
   ```

---

## 🤗 3. Option B: Deployment to Hugging Face Spaces

Hugging Face Spaces offers free CPU Docker hosting ideal for ML/AI portfolio demonstrations.

1. Navigate to [https://huggingface.co/new-space](https://huggingface.co/new-space).
2. Set Space Name: `suryagharsathi-solar`.
3. Choose Space SDK: **Docker** (Blank).
4. Go to **Settings $\rightarrow$ Variables and Secrets**, and add:
   - Secret Name: `GEMINI_API_KEY`, Value: `your_gemini_key`
5. Connect your GitHub repository or mirror to the Hugging Face Git remote:
   ```powershell
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/suryagharsathi-solar
   git push hf main
   ```

---

## 🔄 4. Continuous Deployment (CD) Workflow

Once connected, your deployment enjoys **GitOps Continuous Deployment**:
```
Developer pushes to 'main'
       │
       ▼
 [GitHub Actions CI] ──► Runs Ruff linting + 24 Pytest tests + Docker build
       │
       ▼ (If all tests green)
 [Render / HF Cloud] ──► Automatically pulls new commit & re-deploys container
```

---

## 🔒 5. Security & Cost Protection
- **Zero API Key Leakage:** Keys are injected strictly via host environment variables (`Render Secret Manager`) and never hardcoded in source files or container layers.
- **Spending Limits:** Use free-tier Gemini API quotas (15 requests/min) with our local deterministic fallback ensuring 100% uptime even if external quotas are depleted.
