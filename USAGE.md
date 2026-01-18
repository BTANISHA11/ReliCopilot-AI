# ReliCopilot-AI Usage Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [API Endpoints](#api-endpoints)
3. [Dashboard Usage](#dashboard-usage)
4. [Configuration](#configuration)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/BTANISHA11/ReliCopilot-AI.git
cd ReliCopilot-AI

# Install dependencies
pip install -r requirements.txt

# (Optional) Install and setup Ollama
curl https://ollama.ai/install.sh | sh
ollama pull llama2
```

### Quick Start

**Option 1: Using the start script**
```bash
./start.sh
```

**Option 2: Manual start**
```bash
# Terminal 1: Start API server
python api.py

# Terminal 2: Start dashboard
streamlit run dashboard.py
```

**Option 3: Using Docker Compose**
```bash
docker-compose up
```

## API Endpoints

### Health Check
```bash
GET /health
```

Returns the current health status of the service.

**Example:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-18T10:30:00.000000"
}
```

### Service Info
```bash
GET /
```

Returns basic service information.

**Example:**
```bash
curl http://localhost:8000/
```

### Simulate Request
```bash
GET /api/simulate
```

Triggers a simulated request that may succeed or fail randomly based on configured error rates.

**Example:**
```bash
curl http://localhost:8000/api/simulate
```

**Success Response:**
```json
{
  "status": "success",
  "latency_ms": 523.45,
  "timestamp": "2024-01-18T10:30:00.000000"
}
```

**Error Response:**
```json
{
  "detail": "Internal Server Error: Database connection timeout"
}
```

### Get Telemetry Events
```bash
GET /api/telemetry?limit={limit}&event_type={type}
```

Retrieves telemetry events from the database.

**Parameters:**
- `limit` (optional): Maximum number of events to return (default: 100)
- `event_type` (optional): Filter by event type ("error" or "request")

**Example:**
```bash
# Get last 50 events
curl "http://localhost:8000/api/telemetry?limit=50"

# Get only error events
curl "http://localhost:8000/api/telemetry?event_type=error&limit=10"
```

**Response:**
```json
{
  "count": 2,
  "events": [
    {
      "id": 1,
      "timestamp": "2024-01-18T10:30:00.000000",
      "event_type": "error",
      "endpoint": "/api/simulate",
      "status_code": 500,
      "latency_ms": 1234.56,
      "error_message": "Internal Server Error: Database connection timeout",
      "analysis": "Root cause: Database connection pool exhausted...",
      "extra_data": {"simulated": true}
    }
  ]
}
```

### Get Statistics
```bash
GET /api/stats
```

Returns aggregate statistics about all telemetry events.

**Example:**
```bash
curl http://localhost:8000/api/stats
```

**Response:**
```json
{
  "total_events": 150,
  "error_count": 15,
  "error_rate_percent": 10.0,
  "avg_latency_ms": 856.42
}
```

### Analyze Event
```bash
POST /api/analyze/{event_id}
```

Manually trigger AI analysis for a specific error event.

**Example:**
```bash
curl -X POST http://localhost:8000/api/analyze/5
```

**Response:**
```json
{
  "event_id": 5,
  "analysis": "Root cause: Database connection timeout due to..."
}
```

## Dashboard Usage

Access the dashboard at `http://localhost:8501` after starting the Streamlit server.

### Features

1. **Metrics Overview**
   - Total Events: Total number of telemetry events recorded
   - Error Count: Number of error events
   - Error Rate: Percentage of requests that failed
   - Avg Latency: Average response time in milliseconds

2. **Controls (Sidebar)**
   - Auto-refresh: Toggle automatic data refresh every 5 seconds
   - Events to display: Control number of events shown (10-200)
   - Filter by type: Show all events, only errors, or only requests

3. **Action Buttons**
   - 🎲 Simulate Request: Trigger a test request
   - 🔄 Refresh Data: Manually refresh dashboard data

4. **Event Log**
   - Table view of recent telemetry events
   - Shows timestamp, type, endpoint, status, latency, and errors

5. **AI Failure Analysis**
   - Expandable cards for each error event
   - Detailed error information
   - AI-generated root cause analysis and remediation steps

## Configuration

### Environment Variables

Edit `config.py` or set environment variables:

```bash
# Database
export DATABASE_URL="sqlite+aiosqlite:///telemetry.db"

# API Server
export API_HOST="0.0.0.0"
export API_PORT="8000"

# Ollama LLM
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llama2"

# Dashboard
export DASHBOARD_PORT="8501"

# Simulation Settings
export ERROR_RATE="0.1"        # 10% error rate
export MAX_LATENCY_MS="2000"   # Max 2 seconds latency
```

### Adjusting Error Simulation

To change the types of errors simulated, edit `utils.py`:

```python
errors = [
    (500, "Internal Server Error: Database connection timeout"),
    (503, "Service Unavailable: Downstream service not responding"),
    # Add your custom errors here
]
```

## Examples

### Load Testing Script

Generate traffic to test the reliability monitoring:

```bash
#!/bin/bash
# Generate 100 test requests
for i in {1..100}; do
  curl -s http://localhost:8000/api/simulate > /dev/null
  echo "Request $i completed"
  sleep 0.1
done

# View results
curl http://localhost:8000/api/stats | python -m json.tool
```

### Python Integration

```python
import httpx
import asyncio

async def monitor_service():
    async with httpx.AsyncClient() as client:
        # Trigger a request
        response = await client.get("http://localhost:8000/api/simulate")
        
        # Check stats
        stats = await client.get("http://localhost:8000/api/stats")
        print(stats.json())
        
        # Get recent errors
        errors = await client.get(
            "http://localhost:8000/api/telemetry?event_type=error&limit=5"
        )
        print(errors.json())

asyncio.run(monitor_service())
```

### Using with Existing Services

Integrate with your existing application:

```python
from database import AsyncSessionLocal, TelemetryEvent
import json

async def log_error(endpoint: str, status_code: int, error_msg: str):
    """Log an error to ReliCopilot-AI."""
    async with AsyncSessionLocal() as session:
        event = TelemetryEvent(
            event_type="error",
            endpoint=endpoint,
            status_code=status_code,
            error_message=error_msg,
            extra_data=json.dumps({"source": "my-app"})
        )
        session.add(event)
        await session.commit()
```

## Troubleshooting

### API won't start

**Issue:** Port 8000 is already in use

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill it or use a different port
export API_PORT=8001
python api.py
```

### Dashboard can't connect to API

**Issue:** Dashboard shows "Unable to connect to API"

**Solution:**
1. Verify API is running: `curl http://localhost:8000/health`
2. Check API_BASE_URL in dashboard.py matches your API server
3. Ensure no firewall is blocking localhost connections

### No AI analysis available

**Issue:** Events show "Ollama not available"

**Solution:**
1. Install Ollama: https://ollama.ai/
2. Start Ollama service: `ollama serve`
3. Pull the model: `ollama pull llama2`
4. Verify: `curl http://localhost:11434/api/version`

### Database errors

**Issue:** Database-related errors on startup

**Solution:**
```bash
# Remove existing database and let it recreate
rm telemetry.db
python api.py
```

### High memory usage

**Issue:** Application using too much memory

**Solution:**
1. Reduce telemetry retention by periodically clearing old events
2. Use a smaller Ollama model
3. Adjust query limits in API calls

## Advanced Usage

### Custom Middleware

Add custom telemetry collection:

```python
# In api.py, add to middleware
@app.middleware("http")
async def custom_telemetry(request: Request, call_next):
    # Your custom logic here
    response = await call_next(request)
    return response
```

### Database Cleanup

Periodically clean old events:

```bash
sqlite3 telemetry.db "DELETE FROM telemetry_events WHERE timestamp < datetime('now', '-7 days')"
```

### Export Data

Export telemetry for analysis:

```bash
# Export to CSV
sqlite3 -header -csv telemetry.db "SELECT * FROM telemetry_events" > telemetry.csv

# Export to JSON
curl "http://localhost:8000/api/telemetry?limit=1000" > telemetry.json
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest test_basic.py -v

# Run with coverage
pip install pytest-cov
pytest --cov=. test_basic.py
```

## Performance Tips

1. **Database Optimization**: For high-throughput scenarios, consider PostgreSQL instead of SQLite
2. **Caching**: Enable caching in Streamlit for better dashboard performance
3. **Batch Processing**: Batch telemetry writes for better performance
4. **Async Processing**: Use background tasks for AI analysis to avoid blocking requests

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/BTANISHA11/ReliCopilot-AI/issues
- Documentation: See README.md

---

**Happy Monitoring! 🛡️**
