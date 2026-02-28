"""
Database configuration and session management using SQLAlchemy.

Uses SQLite for v1, easily swappable to PostgreSQL in future versions.
All timestamps are UTC-aware.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base, DeclarativeBase

from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base class for all models
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Database URL
DATABASE_URL = f"sqlite+aiosqlite:///{settings.DATABASE_PATH}"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    # For SQLite in-memory or file-based, use StaticPool
    poolclass=StaticPool if ":memory:" in DATABASE_URL else None,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database by creating all tables."""
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from backend.app.models.user import User  # noqa: F401
        from backend.app.models.conversation import Conversation, Message  # noqa: F401
        from backend.app.models.analytics import ChatLog, DocumentAccess, FeedbackLog  # noqa: F401
        
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created/verified")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get DB session for FastAPI endpoints.
    
    Usage:
        async def my_endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
