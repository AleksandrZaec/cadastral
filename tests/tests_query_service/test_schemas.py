import pytest
from app.query_service.schemas import RequestCreate


class TestRequestSchemas:
    def test_request_create_valid(self):
        """Accepts valid coordinates and cadastral number."""
        obj = RequestCreate(cadastral_number="77:01:0001001:1", latitude=55.75, longitude=37.61)
        assert obj.cadastral_number == "77:01:0001001:1"
        assert obj.latitude == 55.75
        assert obj.longitude == 37.61

    @pytest.mark.parametrize("lat", [-91, 91])
    def test_request_create_invalid_latitude(self, lat):
        """Rejects latitude out of [-90, 90]."""
        with pytest.raises(ValueError):
            RequestCreate(cadastral_number="x", latitude=lat, longitude=0)

    @pytest.mark.parametrize("lon", [-181, 181])
    def test_request_create_invalid_longitude(self, lon):
        """Rejects longitude out of [-180, 180]."""
        with pytest.raises(ValueError):
            RequestCreate(cadastral_number="x", latitude=0, longitude=lon)
