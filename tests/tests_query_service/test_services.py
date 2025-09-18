import pytest
from app.query_service.services import RequestService
from app.query_service.models import Request


class FakeRepo:
    def __init__(self):
        self.created = []

    async def create(self, request: Request) -> Request:
        request.id = len(self.created) + 1
        self.created.append(request)
        return request

    async def update_request_result(self, *, request: Request, response, success):
        request.response = response
        request.success = success
        return request

    async def get_all(self, limit=None, offset=None):
        return list(self.created)[offset or 0: (offset or 0) + (limit or len(self.created))]

    async def get_by_cadastral_number(self, cadastral_number: str, limit=None, offset=None):
        items = [r for r in self.created if r.cadastral_number == cadastral_number]
        return items[offset or 0: (offset or 0) + (limit or len(items))]


class TestRequestService:
    @pytest.mark.asyncio
    async def test_process_request_success(self, monkeypatch):
        """Persists request and marks success on external OK."""

        async def fake_send(payload):
            return True

        import app.query_service.services as services_mod
        monkeypatch.setattr(services_mod, "send_to_external_service", fake_send, raising=True)

        repo = FakeRepo()
        service = RequestService(repo)

        result = await service.process_request("77:01:0001001:1", 55.75, 37.61)
        assert result.id == 1
        assert result.success is True
        assert result.response == {"success": True}

    @pytest.mark.asyncio
    async def test_process_request_timeout(self, monkeypatch):
        """Converts timeout into HTTP 504 error with request id."""
        from app.query_service.utils import ExternalServiceError

        async def fake_send(payload):
            raise ExternalServiceError("timeout")

        import app.query_service.services as services_mod
        monkeypatch.setattr(services_mod, "send_to_external_service", fake_send, raising=True)

        repo = FakeRepo()
        service = RequestService(repo)

        with pytest.raises(Exception) as ei:
            await service.process_request("77:01:0001001:1", 0, 0)
        assert getattr(ei.value, "status_code", None) == 504

    @pytest.mark.asyncio
    async def test_history_methods(self, monkeypatch):
        """Returns lists for all and by cadastral number."""
        repo = FakeRepo()
        service = RequestService(repo)

        r1 = Request(cadastral_number="A", latitude=1, longitude=1, payload={})
        r2 = Request(cadastral_number="B", latitude=2, longitude=2, payload={})
        r1 = await repo.create(r1)
        r2 = await repo.create(r2)
        await repo.update_request_result(request=r1, response={"success": True}, success=True)
        await repo.update_request_result(request=r2, response={"success": False}, success=False)

        all_items = await service.get_history_all()
        assert len(all_items) == 2

        by_a = await service.get_history_by_cadastral_number("A")
        assert len(by_a) == 1
        assert by_a[0].cadastral_number == "A"
