from datetime import datetime, timedelta, UTC
from unittest.mock import patch, Mock
import pytest
from app.services.cache_service import WeatherCache


@pytest.fixture
def cache():
    return WeatherCache(ttl_seconds=300)


def test_cache_set_and_get(cache):
    # Arrange
    cache_key = "test_key"
    test_data = {"temperature": 20}

    # Act
    cache.set(cache_key, test_data)
    result = cache.get(cache_key)

    # Assert
    assert result == test_data


def test_cache_get_nonexistent_key(cache):
    assert cache.get("nonexistent_key") is None


def test_cache_invalidate(cache):
    # Arrange
    cache_key = "test_key"
    test_data = {"temperature": 20}
    cache.set(cache_key, test_data)

    # Act
    cache.invalidate(cache_key)

    # Assert
    assert cache.get(cache_key) is None


def test_cache_clear(cache):
    # Arrange
    test_data = {"key1": {"temp": 20}, "key2": {"temp": 25}}
    for key, data in test_data.items():
        cache.set(key, data)

    # Act
    cache.clear()

    # Assert
    assert all(cache.get(key) is None for key in test_data.keys())


@pytest.mark.parametrize(
    "ttl_seconds,sleep_seconds,should_exist",
    [
        (2, 1, True),  # Data should still exist
        (2, 3, False),  # Data should expire
    ],
)
def test_cache_expiration(ttl_seconds, sleep_seconds, should_exist):
    # Arrange
    cache = WeatherCache(ttl_seconds=ttl_seconds)
    cache_key = "test_key"
    test_data = {"temperature": 20}

    with patch("app.services.cache_service.datetime") as mock_datetime:
        # Set initial time
        initial_time = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        future_time = initial_time + timedelta(seconds=sleep_seconds)

        mock_now = Mock(side_effect=[initial_time, future_time])
        mock_datetime.now = mock_now
        mock_datetime.UTC = UTC

        # Act
        cache.set(cache_key, test_data)
        result = cache.get(cache_key)

        # Assert
        if should_exist:
            assert result == test_data
        else:
            assert result is None


def test_cleanup_expired(cache):
    # Arrange
    with patch("app.services.cache_service.datetime") as mock_datetime:
        initial_time = datetime(2024, 1, 1, 12, 0, tzinfo=UTC)
        future_time = initial_time + timedelta(seconds=10)

        mock_now = Mock(side_effect=[initial_time, initial_time, future_time])
        mock_datetime.now = mock_now
        mock_datetime.UTC = UTC

        # Set some data with different timestamps
        cache.set("fresh_key", "fresh_data")
        cache._cache["expired_key"] = (
            "expired_data",
            initial_time - timedelta(seconds=301),
        )

        # Act
        cache.cleanup_expired()

        # Assert
        assert cache.get("fresh_key") == "fresh_data"
        assert cache.get("expired_key") is None


def test_cache_ttl_initialization():
    # Arrange & Act
    custom_ttl = 600
    cache = WeatherCache(ttl_seconds=custom_ttl)

    # Assert
    assert cache.ttl == timedelta(seconds=custom_ttl)
