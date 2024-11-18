import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.weather_service import WeatherService


@pytest.fixture
def weather_service():
    return WeatherService()


@pytest.fixture
def sample_forecast():
    return {
        "lat": 40.7128,
        "lon": -74.0060,
        "timezone": "America/New_York",
        "current": {"temp": 20.5, "humidity": 65},
    }


@pytest.fixture
async def mock_aiohttp_session():
    # Create mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {}  # Will be overridden in tests

    # Create mock session
    mock_session = MagicMock()
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    # Create mock get response context manager
    mock_get_response = AsyncMock()
    mock_get_response.__aenter__.return_value = mock_response
    mock_get_response.__aexit__.return_value = None

    # Setup get method
    mock_session.get.return_value = mock_get_response

    # Use regular patch instead of async with
    patcher = patch("aiohttp.ClientSession", return_value=mock_session_cm)
    mock = patcher.start()
    yield mock, mock_response
    patcher.stop()


class TestWeatherService:
    async def test_fetch_onecall_data_success(
        self, weather_service, mock_aiohttp_session, sample_forecast
    ):
        """Test successful weather data fetch"""
        # Arrange
        _, mock_response = mock_aiohttp_session
        mock_response.json.return_value = sample_forecast

        # Act
        result = await weather_service.fetch_onecall_data(
            lat=40.7128, lon=-74.0060, units="metric"
        )

        # Assert
        assert result == sample_forecast

    async def test_fetch_onecall_data_error_status(
        self, weather_service, mock_aiohttp_session
    ):
        """Test weather data fetch with error status"""
        # Arrange
        _, mock_response = mock_aiohttp_session
        mock_response.status = 404

        # Act
        result = await weather_service.fetch_onecall_data(
            lat=40.7128, lon=-74.0060, units="metric"
        )

        # Assert
        assert result is None

    async def test_fetch_onecall_data_with_exclude(
        self, weather_service, mock_aiohttp_session, sample_forecast
    ):
        """Test weather data fetch with exclude parameter"""
        # Arrange
        mock_session, mock_response = mock_aiohttp_session
        mock_response.json.return_value = sample_forecast
        exclude = "hourly,daily"

        # Act
        result = await weather_service.fetch_onecall_data(
            lat=40.7128, lon=-74.0060, units="metric", exclude=exclude
        )

        # Assert
        assert result == sample_forecast
        # Verify exclude parameter was included in the request
        mock_get_call = mock_session.return_value.__aenter__.return_value.get.call_args
        assert mock_get_call[1]["params"]["exclude"] == exclude

    async def test_fetch_onecall_data_exception(
        self, weather_service, mock_aiohttp_session
    ):
        """Test weather data fetch with raised exception"""
        # Arrange
        mock_session, _ = mock_aiohttp_session
        mock_session.return_value.__aenter__.return_value.get.side_effect = Exception(
            "Connection error"
        )

        # Act
        result = await weather_service.fetch_onecall_data(
            lat=40.7128, lon=-74.0060, units="metric"
        )

        # Assert
        assert result is None

    async def test_fetch_onecall_data_custom_api_key(
        self, weather_service, mock_aiohttp_session, sample_forecast
    ):
        """Test weather data fetch with custom API key"""
        # Arrange
        mock_session, mock_response = mock_aiohttp_session
        mock_response.json.return_value = sample_forecast
        custom_api_key = "custom_test_key"

        # Act
        result = await weather_service.fetch_onecall_data(
            lat=40.7128, lon=-74.0060, units="metric", api_key=custom_api_key
        )

        # Assert
        assert result == sample_forecast
        mock_get_call = mock_session.return_value.__aenter__.return_value.get.call_args
        assert mock_get_call[1]["params"]["appid"] == custom_api_key
