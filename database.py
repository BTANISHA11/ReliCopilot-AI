"""Database models for telemetry and logging."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

Base = declarative_base()


class TelemetryEvent(Base):
    """Model for storing telemetry events."""
    
    __tablename__ = "telemetry_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_type = Column(String(50), nullable=False)  # e.g., 'request', 'error', 'latency'
    endpoint = Column(String(255), nullable=True)
    status_code = Column(Integer, nullable=True)
    latency_ms = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    analysis = Column(Text, nullable=True)  # AI analysis of the event
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    
    def __repr__(self):
        return f"<TelemetryEvent(id={self.id}, type={self.event_type}, timestamp={self.timestamp})>"


# Create async engine for FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency for getting database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
