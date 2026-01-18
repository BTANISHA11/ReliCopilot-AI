"""FastAPI application for ReliCopilot-AI."""

import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from database import init_db, get_db, TelemetryEvent
from llm_agent import OllamaAgent
from utils import inject_latency, should_simulate_error, generate_random_error, SimulationError
from config import API_HOST, API_PORT
import uvicorn

app = FastAPI(
    title="ReliCopilot-AI",
    description="AI-powered reliability control plane for agent-based systems",
    version="1.0.0"
)

# Initialize LLM agent
llm_agent = OllamaAgent()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()
    print("✓ Database initialized")
    print(f"✓ API server starting on {API_HOST}:{API_PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await llm_agent.close()


@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    """Middleware to capture telemetry for all requests."""
    start_time = datetime.utcnow()
    
    try:
        response = await call_next(request)
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Log successful request
        async with AsyncSessionLocal() as session:
            event = TelemetryEvent(
                event_type="request",
                endpoint=str(request.url.path),
                status_code=response.status_code,
                latency_ms=latency_ms,
                extra_data=json.dumps({"method": request.method})
            )
            session.add(event)
            await session.commit()
        
        return response
        
    except Exception as e:
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Log error
        async with AsyncSessionLocal() as session:
            event = TelemetryEvent(
                event_type="error",
                endpoint=str(request.url.path),
                status_code=500,
                latency_ms=latency_ms,
                error_message=str(e),
                extra_data=json.dumps({"method": request.method})
            )
            session.add(event)
            await session.commit()
        
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "ReliCopilot-AI",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/simulate")
async def simulate_request(db: AsyncSession = Depends(get_db)):
    """
    Simulate a request with potential errors and latency.
    This endpoint demonstrates the reliability monitoring capabilities.
    """
    start_time = datetime.utcnow()
    
    # Inject random latency
    latency_ms = await inject_latency()
    
    # Simulate potential errors
    if should_simulate_error():
        status_code, error_message = generate_random_error()
        
        # Create telemetry event
        event = TelemetryEvent(
            event_type="error",
            endpoint="/api/simulate",
            status_code=status_code,
            latency_ms=latency_ms,
            error_message=error_message,
            extra_data=json.dumps({"simulated": True})
        )
        db.add(event)
        await db.commit()
        
        # Get AI analysis
        analysis = await llm_agent.analyze_failure(
            error_message=error_message,
            endpoint="/api/simulate",
            status_code=status_code,
            context="Simulated error for testing"
        )
        
        # Update event with analysis
        event.analysis = analysis
        await db.commit()
        await db.refresh(event)
        
        raise HTTPException(status_code=status_code, detail=error_message)
    
    # Success case
    return {
        "status": "success",
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/telemetry")
async def get_telemetry(
    limit: int = 100,
    event_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve telemetry events.
    
    Args:
        limit: Maximum number of events to return
        event_type: Filter by event type (optional)
    """
    query = select(TelemetryEvent).order_by(desc(TelemetryEvent.timestamp))
    
    if event_type:
        query = query.where(TelemetryEvent.event_type == event_type)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    return {
        "count": len(events),
        "events": [
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat(),
                "event_type": e.event_type,
                "endpoint": e.endpoint,
                "status_code": e.status_code,
                "latency_ms": e.latency_ms,
                "error_message": e.error_message,
                "analysis": e.analysis,
                "extra_data": json.loads(e.extra_data) if e.extra_data else None
            }
            for e in events
        ]
    }


@app.get("/api/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregate statistics."""
    # Total events
    total_query = select(func.count(TelemetryEvent.id))
    total_result = await db.execute(total_query)
    total_events = total_result.scalar()
    
    # Error count
    error_query = select(func.count(TelemetryEvent.id)).where(
        TelemetryEvent.event_type == "error"
    )
    error_result = await db.execute(error_query)
    error_count = error_result.scalar()
    
    # Average latency
    latency_query = select(func.avg(TelemetryEvent.latency_ms)).where(
        TelemetryEvent.latency_ms.isnot(None)
    )
    latency_result = await db.execute(latency_query)
    avg_latency = latency_result.scalar() or 0
    
    # Error rate
    error_rate = (error_count / total_events * 100) if total_events > 0 else 0
    
    return {
        "total_events": total_events,
        "error_count": error_count,
        "error_rate_percent": round(error_rate, 2),
        "avg_latency_ms": round(avg_latency, 2)
    }


@app.post("/api/analyze/{event_id}")
async def analyze_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """
    Manually trigger AI analysis for a specific event.
    
    Args:
        event_id: ID of the telemetry event to analyze
    """
    query = select(TelemetryEvent).where(TelemetryEvent.id == event_id)
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if not event.error_message:
        raise HTTPException(status_code=400, detail="Event has no error to analyze")
    
    # Get AI analysis
    analysis = await llm_agent.analyze_failure(
        error_message=event.error_message,
        endpoint=event.endpoint or "unknown",
        status_code=event.status_code or 500,
        context=event.extra_data
    )
    
    # Update event
    event.analysis = analysis
    await db.commit()
    await db.refresh(event)
    
    return {
        "event_id": event.id,
        "analysis": analysis
    }


# Import AsyncSessionLocal for middleware
from database import AsyncSessionLocal


if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
