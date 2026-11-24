#!/bin/sh
set -e

# Default port to 8000 or dynamic PORT assigned by cloud provider (Render/Railway/HF)
PORT="${PORT:-8000}"
APP_MODE="${APP_MODE:-api}"

# If custom command arguments are passed to the container, execute them directly
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

echo "=========================================================="
echo " Starting SuryaGharSathi (सूर्याघर साथी)"
echo " Mode: $APP_MODE | Port: $PORT | Provider: ${LLM_PROVIDER:-gemini}"
echo "=========================================================="

if [ "$APP_MODE" = "ui" ]; then
    echo "Launching Streamlit Web Dashboard on port $PORT..."
    exec streamlit run ui/app.py \
        --server.port "$PORT" \
        --server.address "0.0.0.0" \
        --server.headless "true" \
        --browser.gatherUsageStats "false"

elif [ "$APP_MODE" = "both" ]; then
    echo "Launching FastAPI backend in background on port 8000..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &

    echo "Launching Streamlit UI on primary port $PORT..."
    API_URL="http://127.0.0.1:8000" exec streamlit run ui/app.py \
        --server.port "$PORT" \
        --server.address "0.0.0.0" \
        --server.headless "true" \
        --browser.gatherUsageStats "false"

else
    echo "Launching Production FastAPI backend on port $PORT..."
    exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
fi
