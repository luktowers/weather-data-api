import pytest
from unittest.mock import MagicMock, PropertyMock, patch
from app.services.storage_service import StorageService
from datetime import UTC, datetime, timedelta


@pytest.fixture
def storage_service():
    return StorageService()


@pytest.fixture
def sample_forecast_data():
    return {
        "lat": 40.7128,
        "lon": -74.0060,
        "timezone": "America/New_York",
        "current": {"temp": 20.5, "humidity": 65},
    }


@pytest.fixture
def mock_dynamodb_table():
    mock_table = MagicMock()
    mock_table.get_item.return_value = {
        "Item": {
            "forecast_data": '{"key": "value"}',
            "ttl": int((datetime.now(UTC) + timedelta(minutes=10)).timestamp()),
        }
    }
    with patch(
        "app.services.storage_service.StorageService.table", new_callable=PropertyMock
    ) as mock_table_property:
        mock_table_property.return_value = mock_table
        yield mock_table


class TestStorageService:
    async def test_store_forecast_success(
        self, storage_service, sample_forecast_data, mock_dynamodb_table
    ):
        # Arrange
        lat, lon, units = 40.7128, -74.0060, "metric"

        # Act
        result = await storage_service.store_forecast(
            lat, lon, units, sample_forecast_data
        )

        # Assert
        assert result is True
        mock_dynamodb_table.put_item.assert_called_once()

    async def test_store_forecast_failure(
        self, storage_service, sample_forecast_data, mock_dynamodb_table
    ):
        # Arrange
        lat, lon, units = 40.7128, -74.0060, "metric"
        mock_dynamodb_table.put_item.side_effect = Exception("Error storing data")

        # Act
        result = await storage_service.store_forecast(
            lat, lon, units, sample_forecast_data
        )

        # Assert
        assert result is False

    async def test_get_forecast_success(
        self, storage_service, sample_forecast_data, mock_dynamodb_table
    ):
        # Arrange
        lat, lon, units = 40.7128, -74.0060, "metric"
        mock_dynamodb_table.get_item.return_value = {
            "Item": {
                "forecast_data": '{"key": "value"}',
                "ttl": int((datetime.now(UTC) + timedelta(minutes=10)).timestamp()),
            }
        }

        # Act
        result = await storage_service.get_forecast(lat, lon, units)

        # Assert
        assert result == {"key": "value"}
        mock_dynamodb_table.get_item.assert_called_once_with(
            Key={"location_key": f"{lat}_{lon}_{units}"}
        )

    async def test_get_forecast_not_found(self, storage_service, mock_dynamodb_table):
        # Arrange
        lat, lon, units = 40.7128, -74.0060, "metric"
        mock_dynamodb_table.get_item.return_value = {}

        # Act
        result = await storage_service.get_forecast(lat, lon, units)

        # Assert
        assert result is None

    async def test_get_forecast_expired(
        self, storage_service, sample_forecast_data, mock_dynamodb_table
    ):
        # Arrange
        lat, lon, units = 40.7128, -74.0060, "metric"
        expired_time = datetime.now(UTC) - timedelta(minutes=10)
        mock_dynamodb_table.get_item.return_value = {
            "Item": {
                "forecast_data": '{"key": "value"}',
                "ttl": int(expired_time.timestamp()),
            }
        }

        # Act
        result = await storage_service.get_forecast(lat, lon, units)

        # Assert
        assert result is None

    async def test_get_forecast_failure(self, storage_service, mock_dynamodb_table):
        # Arrange
        lat, lon, units = 40.7128, -74.0060, "metric"
        mock_dynamodb_table.get_item.side_effect = Exception("Error retrieving data")

        # Act
        result = await storage_service.get_forecast(lat, lon, units)

        # Assert
        assert result is None
