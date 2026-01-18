#!/bin/bash

# Start script for ReliCopilot-AI services
# This script starts both the API server and the dashboard

echo "🛡️  Starting ReliCopilot-AI..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Check if dependencies are installed
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

echo "✓ Dependencies installed"

# Check if Ollama is running (optional)
if curl -s http://localhost:11434/api/version &> /dev/null; then
    echo "✓ Ollama is running"
else
    echo "⚠️  Ollama is not running (AI analysis will be unavailable)"
    echo "   Install from: https://ollama.ai/"
fi

echo ""
echo "Starting services..."
echo "  - API Server: http://localhost:8000"
echo "  - Dashboard: http://localhost:8501"
echo ""

# Start API server in background
python3 api.py &
API_PID=$!

# Wait for API to be ready
echo "Waiting for API server to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health &> /dev/null; then
        echo "✓ API server is ready"
        break
    fi
    sleep 1
done

# Start Streamlit dashboard
streamlit run dashboard.py

# Cleanup on exit
trap "kill $API_PID 2>/dev/null" EXIT
