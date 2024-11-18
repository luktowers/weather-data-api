from datetime import datetime, timedelta, UTC
from typing import Dict, Optional, Any


class WeatherCache:
    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, cache_key: str) -> Optional[Any]:
        if cache_key not in self._cache:
            return None

        data, timestamp = self._cache[cache_key]
        if datetime.now(UTC) - timestamp > self.ttl:
            del self._cache[cache_key]
            return None

        return data

    def set(self, cache_key: str, data: Any) -> None:
        self._cache[cache_key] = (data, datetime.now(UTC))

    def invalidate(self, cache_key: str) -> None:
        """Remove specific key from cache"""
        if cache_key in self._cache:
            del self._cache[cache_key]

    def clear(self) -> None:
        """Remove all entries from cache"""
        self._cache.clear()

    def cleanup_expired(self) -> None:
        """Remove all expired entries from cache"""
        current_time = datetime.now(UTC)
        expired_keys = [
            key
            for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp > self.ttl
        ]
        for key in expired_keys:
            del self._cache[key]
