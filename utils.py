"""Utility functions for error simulation and latency injection."""

import random
import asyncio
from typing import Optional
from config import ERROR_RATE, MAX_LATENCY_MS


class SimulationError(Exception):
    """Custom exception for simulated errors."""
    pass


async def inject_latency(max_latency_ms: int = MAX_LATENCY_MS) -> float:
    """
    Inject random latency into a request.
    
    Args:
        max_latency_ms: Maximum latency in milliseconds
        
    Returns:
        Actual latency injected in milliseconds
    """
    latency_ms = random.uniform(0, max_latency_ms)
    await asyncio.sleep(latency_ms / 1000.0)
    return latency_ms


def should_simulate_error(error_rate: float = ERROR_RATE) -> bool:
    """
    Determine if an error should be simulated.
    
    Args:
        error_rate: Probability of error (0.0 to 1.0)
        
    Returns:
        True if error should be simulated
    """
    return random.random() < error_rate


def generate_random_error() -> tuple[int, str]:
    """
    Generate a random error.
    
    Returns:
        Tuple of (status_code, error_message)
    """
    errors = [
        (500, "Internal Server Error: Database connection timeout"),
        (503, "Service Unavailable: Downstream service not responding"),
        (429, "Too Many Requests: Rate limit exceeded"),
        (504, "Gateway Timeout: Upstream service timeout"),
        (500, "Internal Server Error: Null pointer exception"),
        (502, "Bad Gateway: Invalid response from upstream"),
        (500, "Internal Server Error: Out of memory"),
    ]
    return random.choice(errors)
