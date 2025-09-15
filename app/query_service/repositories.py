from abc import ABC, abstractmethod
from typing import List
from app.query_service.models import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class AbstractRequestRepository(ABC):
    """An abstract repository for working with cadastral queries."""

    @abstractmethod
    async def create(self, request: Request) -> Request:
        """Creates a record of the request."""
        pass

    @abstractmethod
    async def get_all(self) -> List[Request]:
        """Returns all requests."""
        pass

    @abstractmethod
    async def get_by_cadastral_number(self, cadastral_number: str) -> List[Request]:
        """Returns all requests by cadastral number."""
        pass


class SQLAlchemyRequestRepository(AbstractRequestRepository):
    """Repository implementation using SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, request: Request) -> Request:
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request

    async def get_all(self) -> List[Request]:
        result = await self.session.execute(select(Request))
        return result.scalars().all()

    async def get_by_cadastral_number(self, cadastral_number: str) -> List[Request]:
        result = await self.session.execute(
            select(Request).where(Request.cadastral_number == cadastral_number)
        )
        return result.scalars().all()
