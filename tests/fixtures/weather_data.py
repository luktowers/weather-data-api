import pytest


@pytest.fixture
def sample_forecast():
    return {
        "lat": 40.7128,
        "lon": -74.0060,
        "timezone": "America/New_York",
        "current": {"temp": 20.5, "humidity": 65},
    }


@pytest.fixture
def sample_error_response():
    return {"cod": 404, "message": "Weather forecast data not found"}
