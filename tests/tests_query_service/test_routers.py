from fastapi.testclient import TestClient


class TestRouters:
    def test_ping(self, client: TestClient):
        """Responds ok from health check endpoint."""
        r = client.get("/ping")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_query_endpoint(self, client: TestClient):
        """Creates request and returns persisted entity."""
        r = client.post("/query", json={"cadastral_number": "A", "latitude": 1.0, "longitude": 2.0})
        assert r.status_code == 201
        data = r.json()
        assert data["cadastral_number"] == "A"
        assert data["success"] is True

    def test_history_endpoints(self, client: TestClient):
        """Lists all and filtered history entries."""
        client.post("/query", json={"cadastral_number": "A", "latitude": 1.0, "longitude": 2.0})
        client.post("/query", json={"cadastral_number": "B", "latitude": 1.0, "longitude": 2.0})

        r_all = client.get("/history?limit=10&offset=0")
        assert r_all.status_code == 200
        data_all = r_all.json()
        assert len(data_all) == 2
        assert all("created_at" in item for item in data_all)

        r_a = client.get("/history/A")
        assert r_a.status_code == 200
        items = r_a.json()
        assert all(item["cadastral_number"] == "A" for item in items)
