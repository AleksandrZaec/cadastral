from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.query_service.models import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.core.logging import get_logger


class AbstractRequestRepository(ABC):
    """An abstract repository for working with cadastral queries."""

    @abstractmethod
    async def create(self, request: Request) -> Request:
        """Creates a record of the request."""
        pass

    @abstractmethod
    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Request]:
        """Returns all requests with optional pagination."""
        pass

    @abstractmethod
    async def get_by_cadastral_number(self, cadastral_number: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Request]:
        """Returns requests by cadastral number with optional pagination."""
        pass

    @abstractmethod
    async def update_request_result(self, *, request: Request, response: Optional[Dict[str, Any]], success: Optional[bool]) -> Request:
        """Update a request's response and success flags with safe commit/rollback."""
        pass


class SQLAlchemyRequestRepository(AbstractRequestRepository):
    """Repository implementation using SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with an active async session."""
        self.session: AsyncSession = session
        self.logger = get_logger("repo")

    async def create(self, request: Request) -> Request:
        try:
            self.logger.debug("Creating request", extra={"cadastral_number": request.cadastral_number})
            self.session.add(request)
            await self.session.commit()
            await self.session.refresh(request)
            self.logger.info("Request created", extra={"request_id": request.id})
            return request
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Create failed", extra={"error": str(e)})
            raise e

    async def update_request_result(self, *, request: Request, response: Optional[Dict[str, Any]], success: Optional[bool]) -> Request:
        try:
            request.response = response
            request.success = success
            await self.session.commit()
            await self.session.refresh(request)
            self.logger.debug("Request updated", extra={"request_id": request.id, "success": success})
            return request
        except SQLAlchemyError as e:
            await self.session.rollback()
            self.logger.error("Update failed", extra={"request_id": getattr(request, 'id', None), "error": str(e)})
            raise e

    async def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Request]:
        query = select(Request).order_by(Request.created_at.desc())
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        result = await self.session.execute(query)
        items = result.scalars().all()
        self.logger.debug("Fetched all requests", extra={"limit": limit, "offset": offset, "count": len(items)})
        return items

    async def get_by_cadastral_number(self, cadastral_number: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Request]:
        query = select(Request).where(Request.cadastral_number == cadastral_number).order_by(Request.created_at.desc())
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        result = await self.session.execute(query)
        items = result.scalars().all()
        self.logger.debug("Fetched by cadastral", extra={"cadastral_number": cadastral_number, "limit": limit, "offset": offset, "count": len(items)})
        return items
