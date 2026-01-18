# 🛡️ ReliCopilot-AI

An AI-powered reliability control plane for agent-based systems. Explain failures before they become outages.

## Overview

ReliCopilot-AI is a minimal, zero-cost reliability monitoring solution that combines:
- **FastAPI** backend for telemetry collection
- **SQLite** for persistent logging
- **Ollama** local LLM for intelligent failure analysis
- **Streamlit** dashboard for real-time visualization
- Built-in error simulation and latency injection for testing

## Features

✨ **Key Capabilities:**
- 📊 Real-time telemetry collection and monitoring
- 🤖 AI-powered failure analysis using local LLM (no API costs)
- 🎲 Simulated errors and latency for testing reliability patterns
- 📈 Beautiful dashboard with metrics and event visualization
- 💾 Persistent SQLite logging for historical analysis
- 🔌 RESTful API for easy integration

## Architecture

```
┌─────────────────┐
│   Streamlit     │  (Port 8501)
│   Dashboard     │  
└────────┬────────┘
         │
         │ HTTP
         ▼
┌─────────────────┐
│   FastAPI       │  (Port 8000)
│   Backend       │  
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────┐
│ SQLite │ │  Ollama  │
│  DB    │ │   LLM    │
└────────┘ └──────────┘
```

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) (for AI analysis)

## Quick Start

### 1. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/BTANISHA11/ReliCopilot-AI.git
cd ReliCopilot-AI

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Setup Ollama (Optional but Recommended)

```bash
# Install Ollama from https://ollama.ai/

# Pull the llama2 model
ollama pull llama2

# Verify Ollama is running
curl http://localhost:11434/api/version
```

> **Note:** The system works without Ollama, but AI failure analysis will not be available.

### 3. Start the API Server

```bash
# Start FastAPI backend
python api.py
```

The API will be available at `http://localhost:8000`

### 4. Start the Dashboard

In a new terminal:

```bash
# Start Streamlit dashboard
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

## Usage

### API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `GET /api/simulate` - Trigger a simulated request (may fail randomly)
- `GET /api/telemetry?limit=100&event_type=error` - Retrieve telemetry events
- `GET /api/stats` - Get aggregate statistics
- `POST /api/analyze/{event_id}` - Manually trigger AI analysis for an event

### Dashboard Features

1. **Metrics Overview**: View total events, error count, error rate, and average latency
2. **Simulate Requests**: Click "🎲 Simulate Request" to generate test traffic
3. **Event Log**: View recent telemetry events with filtering options
4. **AI Analysis**: See AI-powered root cause analysis for errors

### Testing Error Simulation

```bash
# Trigger multiple simulated requests
for i in {1..20}; do
  curl http://localhost:8000/api/simulate
  echo ""
done

# View telemetry
curl http://localhost:8000/api/telemetry?limit=10

# Get statistics
curl http://localhost:8000/api/stats
```

## Configuration

Edit `config.py` or use environment variables:

```python
# Database
DATABASE_URL = "sqlite+aiosqlite:///telemetry.db"

# API Server
API_HOST = "0.0.0.0"
API_PORT = 8000

# Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama2"

# Simulation
ERROR_RATE = 0.1  # 10% chance of error
MAX_LATENCY_MS = 2000  # Max 2 seconds
```

## Project Structure

```
ReliCopilot-AI/
├── api.py              # FastAPI backend application
├── dashboard.py        # Streamlit dashboard
├── database.py         # SQLAlchemy models and DB setup
├── llm_agent.py        # Ollama LLM integration
├── utils.py            # Error simulation utilities
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when available)
pytest
```

### Customizing Error Simulation

Edit `utils.py` to add custom error scenarios:

```python
errors = [
    (500, "Internal Server Error: Custom error message"),
    (503, "Service Unavailable: Custom unavailable message"),
    # Add more...
]
```

## Why ReliCopilot-AI?

- **Zero Cost**: Uses local LLM (Ollama) instead of paid APIs
- **Privacy First**: All data stays on your machine
- **Fast Setup**: Under 5 minutes from clone to running
- **Production Ready**: Built with FastAPI and proper async patterns
- **Educational**: Clean code structure for learning reliability patterns

## Troubleshooting

### Ollama Connection Issues

If you see "Ollama not available":
1. Install Ollama from https://ollama.ai/
2. Run `ollama serve` to start the server
3. Run `ollama pull llama2` to download the model

### Database Issues

If you encounter database errors:
```bash
# Delete the database and restart
rm telemetry.db
python api.py
```

### Port Conflicts

If ports 8000 or 8501 are in use:
```bash
# Change ports via environment variables
export API_PORT=8001
export DASHBOARD_PORT=8502
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Dashboard powered by [Streamlit](https://streamlit.io/)
- AI analysis via [Ollama](https://ollama.ai/)

---

**Built for developers who want to understand failures before they become outages** 🚀
