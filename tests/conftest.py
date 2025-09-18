import pytest
import pytest_asyncio


@pytest.fixture(autouse=True, scope="function")
def _no_httpx_prod_calls(monkeypatch):
    import httpx

    async def _blocked(*args, **kwargs):
        raise AssertionError("HTTPX call attempted without mock in tests")

    monkeypatch.setattr(httpx.AsyncClient, "post", _blocked, raising=True)


@pytest_asyncio.fixture(scope="function")
async def session():
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.core.db import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as s:
        yield s

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    from app.query_service.dependencies import get_request_service
    from app.query_service.services import RequestService
    from app.query_service.models import Request

    class _FakeRepo:
        def __init__(self):
            self.items = []

        async def create(self, request: Request) -> Request:
            request.id = len(self.items) + 1
            # ensure required timestamp for response model
            from datetime import datetime, timezone
            if getattr(request, "created_at", None) is None:
                request.created_at = datetime.now(timezone.utc)
            self.items.append(request)
            return request

        async def update_request_result(self, *, request: Request, response, success):
            request.response = response
            request.success = success
            return request

        async def get_all(self, limit=None, offset=None):
            return self.items[offset or 0 : (offset or 0) + (limit or len(self.items))]

        async def get_by_cadastral_number(self, cadastral_number: str, limit=None, offset=None):
            items = [r for r in self.items if r.cadastral_number == cadastral_number]
            return items[offset or 0 : (offset or 0) + (limit or len(items))]

    class _FakeService(RequestService):
        async def process_request(self, cadastral_number: str, latitude=None, longitude=None):
            req = Request(cadastral_number=cadastral_number, latitude=latitude, longitude=longitude, payload={})
            req = await self.repository.create(req)
            return await self.repository.update_request_result(request=req, response={"success": True}, success=True)

    repo = _FakeRepo()
    service = _FakeService(repo)

    app.dependency_overrides[get_request_service] = lambda: service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

