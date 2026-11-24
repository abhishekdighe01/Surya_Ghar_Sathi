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

Render provides native Docker support and can build your container directly from GitHub.

### Method 1: Deploy as a Single Web Service (Best for Free Tier)
Deploy both the Streamlit UI and FastAPI backend in a single free Render Web Service:

1. **Sign in to Render:** Go to [dashboard.render.com](https://dashboard.render.com) and log in with your GitHub account.
2. **Create New Web Service:**
   - Click **"New +"** (top-right) $\rightarrow$ select **"Web Service"**.
   - Select your repository: `abhishekdighe01/Surya_Ghar_Sathi`.
3. **Configure the Service:**
   - **Name:** `suryagharsathi`
   - **Region:** Choose Oregon (US West) or Singapore.
   - **Runtime:** **Docker** (Render automatically detects your [Dockerfile](file:///e:/SuryaGharSathi/Dockerfile)).
   - **Instance Type:** **Free** (0.5 CPU, 512 MB RAM).
4. **Environment Variables:**
   - Click **"Add Environment Variable"** and configure:
     - `GEMINI_API_KEY`: `<your_google_gemini_api_key>`
     - `APP_MODE`: `both` (runs FastAPI backend on port 8000 and Streamlit UI on public port `$PORT`) or `ui` (runs the complete Streamlit UI with local in-memory fallback)
     - `LLM_PROVIDER`: `gemini`
5. **Click "Deploy Web Service":**
   - Render builds the Docker image automatically, runs `entrypoint.sh`, binds to `$PORT`, and gives you a free HTTPS link:
     ```text
     https://suryagharsathi.onrender.com
     ```

---

### Method 2: Deploy via Blueprint (`render.yaml`)
If you prefer managing multi-service deployments via Infrastructure-as-Code:

1. Go to [dashboard.render.com](https://dashboard.render.com) $\rightarrow$ Click **"New +"** $\rightarrow$ select **"Blueprint"**.
2. Select your repository `abhishekdighe01/Surya_Ghar_Sathi`.
3. Render reads [render.yaml](file:///e:/SuryaGharSathi/render.yaml) and displays both services:
   - `suryagharsathi-api` (FastAPI REST service with `/docs` and `/health`)
   - `suryagharsathi-ui` (Streamlit homeowner dashboard)
4. Set `GEMINI_API_KEY` in the prompt and click **"Apply"**.
5. Render will provision both services in parallel.

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
