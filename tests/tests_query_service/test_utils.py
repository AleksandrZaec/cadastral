import pytest
from app.query_service.utils import send_to_external_service, ExternalServiceError


class DummyResponse:
    def __init__(self, status_code: int, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            import httpx
            raise httpx.HTTPStatusError("error", request=None, response=None)

    def json(self):
        return self._json_data


class TestExternalUtils:
    @pytest.mark.asyncio
    async def test_send_to_external_service_success(self, monkeypatch):
        """Returns True on valid 200 JSON response with success flag."""
        async def fake_post(self, url, json):
            return DummyResponse(200, {"success": True})

        import httpx
        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post, raising=True)

        ok = await send_to_external_service({"a": 1})
        assert ok is True

    @pytest.mark.asyncio
    async def test_send_to_external_service_invalid_response(self, monkeypatch):
        """Raises ExternalServiceError for missing success in response body."""
        async def fake_post(self, url, json):
            return DummyResponse(200, {"foo": "bar"})

        import httpx
        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post, raising=True)

        with pytest.raises(ExternalServiceError) as ei:
            await send_to_external_service({})
        assert "invalid_response" in str(ei.value)

    @pytest.mark.asyncio
    async def test_send_to_external_service_timeout(self, monkeypatch):
        """Raises ExternalServiceError on timeout from httpx client."""
        import httpx

        async def fake_post(self, url, json):
            raise httpx.TimeoutException("timeout")

        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post, raising=True)

        with pytest.raises(ExternalServiceError) as ei:
            await send_to_external_service({})
        assert "timeout" in str(ei.value)

    @pytest.mark.asyncio
    async def test_send_to_external_service_http_error(self, monkeypatch):
        """Wraps httpx HTTPError into ExternalServiceError with prefix."""
        import httpx

        async def fake_post(self, url, json):
            raise httpx.HTTPError("boom")

        monkeypatch.setattr(httpx.AsyncClient, "post", fake_post, raising=True)

        with pytest.raises(ExternalServiceError) as ei:
            await send_to_external_service({})
        assert "http_error" in str(ei.value)


