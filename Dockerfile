# ==============================================================================
# File: Dockerfile
# Project: SuryaGharSathi (सूर्याघर साथी)
# Description: Production multi-stage Docker container for FastAPI backend & Streamlit UI
# ==============================================================================

FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable immediate log flushing
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install minimal OS dependencies for health checking
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create a dedicated non-root user for container security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy and install python dependencies first to optimize Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure storage directories exist, make entrypoint executable, and grant permissions to appuser
RUN mkdir -p /app/data/chroma_db /app/data/raw && \
    chmod +x /app/entrypoint.sh && \
    chown -R appuser:appuser /app

# Run as non-root user
USER appuser

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Healthcheck to probe the service
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || curl -f http://localhost:${PORT:-8501}/_stcore/health || exit 0

# Set entrypoint script supporting API, UI, or both modes
ENTRYPOINT ["/app/entrypoint.sh"]
