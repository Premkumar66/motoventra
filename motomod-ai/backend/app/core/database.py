"""
MotoMod AI — Database Engine & Session Management
Async SQLAlchemy 2.0 with connection pooling
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, MappedColumn
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


from app.models.base import Base


def _create_engine(url: str, **kwargs) -> AsyncEngine:
    """Create the async SQLAlchemy engine."""
    engine_kwargs = {
        "echo": settings.is_development,
        **kwargs,
    }
    if "sqlite" not in url:
        engine_kwargs.update({
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        })
    return create_async_engine(url, **engine_kwargs)


# Primary async engine
engine: AsyncEngine = _create_engine(settings.DATABASE_URL)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.
    Handles commit/rollback and ensures session closure.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("database_error", error=str(e), exc_info=True)
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions outside of FastAPI request context.
    Used in Celery tasks and background processes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error("database_context_error", error=str(e), exc_info=True)
            raise
        finally:
            await session.close()


async def check_database_connection() -> bool:
    """Health check for database connectivity."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        return False


async def create_tables() -> None:
    """Create all tables (used in development/testing)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_tables_created")


async def dispose_engine() -> None:
    """Dispose of the engine pool (used during shutdown)."""
    await engine.dispose()
    logger.info("database_engine_disposed")
