import pytest
from app.query_service.models import Request
from app.query_service.repositories import SQLAlchemyRequestRepository


class TestSQLAlchemyRequestRepository:
    @pytest.mark.asyncio
    async def test_create_and_get_all(self, session):
        """Creates a row and fetches it via get_all."""
        repo = SQLAlchemyRequestRepository(session)

        r = Request(cadastral_number="X", latitude=1.0, longitude=2.0, payload={"a": 1})
        r = await repo.create(r)
        assert r.id is not None

        items = await repo.get_all()
        assert len(items) == 1
        assert items[0].cadastral_number == "X"

    @pytest.mark.asyncio
    async def test_get_by_cadastral_and_update(self, session):
        """Filters by cadastral number and updates result fields."""
        repo = SQLAlchemyRequestRepository(session)
        r1 = await repo.create(Request(cadastral_number="A", payload={}))
        r2 = await repo.create(Request(cadastral_number="B", payload={}))

        a_items = await repo.get_by_cadastral_number("A")
        assert len(a_items) == 1
        assert a_items[0].id == r1.id

        updated = await repo.update_request_result(request=r1, response={"success": True}, success=True)
        assert updated.success is True
        assert updated.response == {"success": True}
