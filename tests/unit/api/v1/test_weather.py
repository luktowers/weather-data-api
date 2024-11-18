import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch
from app.main import app


# Test data should be in a separate fixture file
@pytest.fixture
def sample_forecast():
    return {
        "lat": 40.7128,
        "lon": -74.0060,
        "timezone": "America/New_York",
        "current": {"temp": 20.5, "humidity": 65},
    }


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_weather_service():
    with patch("app.api.v1.weather.weather_service") as mock:
        mock.fetch_onecall_data = AsyncMock(return_value=None)  # Default to None
        mock.api_key = "test_key"
        yield mock


@pytest.fixture
def mock_cache_service():
    with patch("app.api.v1.weather.weather_cache") as mock:
        # Use Mock instead of lambda for better assertion capabilities
        mock.get = Mock(return_value=None)
        mock.set = Mock()
        yield mock


@pytest.fixture
def mock_storage_service():
    with patch("app.api.v1.weather.storage_service") as mock:
        mock.get_forecast = AsyncMock(return_value=None)
        mock.store_forecast = AsyncMock(return_value=True)
        yield mock


class TestWeatherForecast:
    """Group related tests in a class for better organization"""

    def test_get_weather_forecast_success(
        self,
        client,
        mock_weather_service,
        mock_cache_service,
        mock_storage_service,
        sample_forecast,
    ):
        """Test successful weather forecast retrieval from API"""
        # Arrange
        mock_weather_service.fetch_onecall_data.return_value = sample_forecast

        # Act
        response = client.get(
            "/api/v1/weather/forecast/coordinates",
            params={"lat": 40.7128, "lon": -74.0060},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == sample_forecast

        # Verify the flow
        mock_cache_service.get.assert_called_once_with("onecall_40.7128_-74.006_metric")
        mock_storage_service.get_forecast.assert_awaited_once_with(
            40.7128, -74.0060, "metric"
        )
        mock_weather_service.fetch_onecall_data.assert_awaited_once()
        mock_cache_service.set.assert_called_once_with(
            "onecall_40.7128_-74.006_metric", sample_forecast
        )

    def test_get_weather_forecast_from_cache(
        self,
        client,
        mock_weather_service,
        mock_cache_service,
        mock_storage_service,
        sample_forecast,
    ):
        """Test weather forecast retrieval from cache"""
        # Arrange
        mock_cache_service.get.return_value = sample_forecast

        # Act
        response = client.get(
            "/api/v1/weather/forecast/coordinates",
            params={"lat": 40.7128, "lon": -74.0060},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == sample_forecast

        # Verify cache hit and no further calls
        mock_cache_service.get.assert_called_once()
        mock_storage_service.get_forecast.assert_not_awaited()
        mock_weather_service.fetch_onecall_data.assert_not_awaited()

    def test_get_weather_forecast_from_storage(
        self,
        client,
        mock_weather_service,
        mock_cache_service,
        mock_storage_service,
        sample_forecast,
    ):
        """Test weather forecast retrieval from storage"""
        # Arrange
        mock_storage_service.get_forecast.return_value = sample_forecast

        # Act
        response = client.get(
            "/api/v1/weather/forecast/coordinates",
            params={"lat": 40.7128, "lon": -74.0060},
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == sample_forecast

        # Verify storage hit and cache update
        mock_cache_service.get.assert_called_once()
        mock_storage_service.get_forecast.assert_awaited_once()
        mock_weather_service.fetch_onecall_data.assert_not_awaited()
        mock_cache_service.set.assert_called_once_with(
            "onecall_40.7128_-74.006_metric", sample_forecast
        )

    @pytest.mark.parametrize(
        "lat,lon,expected_status",
        [
            (91, 0, 422),  # Invalid latitude
            (-91, 0, 422),  # Invalid latitude
            (0, 181, 422),  # Invalid longitude
            (0, -181, 422),  # Invalid longitude
        ],
    )
    def test_get_weather_forecast_invalid_coordinates(
        self, client, lat, lon, expected_status
    ):
        """Test weather forecast retrieval with invalid coordinates"""
        # Act
        response = client.get(
            "/api/v1/weather/forecast/coordinates", params={"lat": lat, "lon": lon}
        )

        # Assert
        assert response.status_code == expected_status

    def test_get_weather_forecast_not_found(
        self, client, mock_weather_service, mock_cache_service, mock_storage_service
    ):
        """Test weather forecast not found scenario"""
        # Arrange
        mock_weather_service.fetch_onecall_data.return_value = None

        # Act
        response = client.get(
            "/api/v1/weather/forecast/coordinates",
            params={"lat": 40.7128, "lon": -74.0060},
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Weather forecast data not found"}

        # Verify the flow
        mock_cache_service.get.assert_called_once()
        mock_storage_service.get_forecast.assert_awaited_once()
        mock_weather_service.fetch_onecall_data.assert_awaited_once()

    @pytest.mark.parametrize(
        "units,exclude,expected_exclude",
        [
            ("imperial", "hourly,daily", "hourly,daily"),
            ("standard", "current,minutely", "current,minutely"),
            ("metric", None, None),  # Added expected_exclude parameter
        ],
    )
    def test_get_weather_forecast_with_parameters(
        self,
        client,
        mock_weather_service,
        mock_cache_service,
        mock_storage_service,
        sample_forecast,
        units,
        exclude,
        expected_exclude,  # Added parameter
    ):
        """Test weather forecast retrieval with different parameters"""
        # Arrange
        mock_weather_service.fetch_onecall_data.return_value = sample_forecast

        # Act
        params = {
            "lat": 40.7128,
            "lon": -74.0060,
            "units": units,
        }
        # Only add exclude parameter if it's not None
        if exclude is not None:
            params["exclude"] = exclude

        response = client.get("/api/v1/weather/forecast/coordinates", params=params)

        # Assert
        assert response.status_code == 200

        # Build expected args dict
        expected_args = {
            "lat": 40.7128,
            "lon": -74.0060,
            "units": units,
            "api_key": "test_key",
        }
        if expected_exclude is not None:
            expected_args["exclude"] = expected_exclude

        assert mock_weather_service.fetch_onecall_data.call_args[1] == expected_args
