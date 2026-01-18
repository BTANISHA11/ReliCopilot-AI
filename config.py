"""Configuration management for ReliCopilot-AI."""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/telemetry.db")

# API configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

# Dashboard configuration
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))

# Simulation configuration
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.1"))  # 10% error rate
MAX_LATENCY_MS = int(os.getenv("MAX_LATENCY_MS", "2000"))  # Max 2 seconds latency
