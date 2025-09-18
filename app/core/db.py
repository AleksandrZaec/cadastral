from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings
from app.core.logging import get_logger

Base = declarative_base()

engine = create_async_engine(settings.DB_URL, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

logger = get_logger("db")


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an `AsyncSession`."""
    async with AsyncSessionLocal() as session:
        logger.debug("DB session opened")
        try:
            yield session
        finally:
            await session.close()
            logger.debug("DB session closed")
