from fastapi import Depends
from app.query_service.services import RequestService
from app.query_service.repositories import SQLAlchemyRequestRepository
from app.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger


logger = get_logger("deps")


async def get_request_service(db: AsyncSession = Depends(get_db)) -> RequestService:
    """Provide a `RequestService` bound to current DB session."""
    # Keep logs low-noise on hot path
    repo = SQLAlchemyRequestRepository(db)
    service = RequestService(repo)
    return service
