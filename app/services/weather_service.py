import aiohttp
import logging
from datetime import datetime
from typing import Dict, Optional
from app.config import settings
from app.models.weather import WeatherData

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall"

    async def fetch_weather_data(self, location_id: str) -> Optional[WeatherData]:
        """Fetch weather data for a given location ID."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/weather"
                params = {
                    "id": location_id,
                    "appid": self.api_key,
                    "units": "metric",  # Use metric units
                }

                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Error fetching weather data: {response.status}")
                        return None

                    data = await response.json()
                    return self._parse_weather_data(data, location_id)

        except Exception as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None

    def _parse_weather_data(self, data: Dict, location_id: str) -> WeatherData:
        """Parse OpenWeatherMap JSON response into WeatherData model."""
        return WeatherData(
            location_id=location_id,
            temperature=data["main"]["temp"],
            humidity=data["main"]["humidity"],
            condition=data["weather"][0]["main"],
            timestamp=datetime.utcnow(),
            wind_speed=data["wind"]["speed"],
            pressure=data["main"]["pressure"],
        )

    async def fetch_onecall_data(
        self,
        lat: float,
        lon: float,
        units: str = "metric",
        exclude: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Fetch weather data from OpenWeather OneCall API 3.0"""
        base_url = "https://api.openweathermap.org/data/3.0/onecall"

        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key
            or self.api_key,  # Use provided api_key or fall back to self.api_key
            "units": units,
        }

        if exclude is not None:
            params["exclude"] = exclude

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    logger.error(f"OpenWeather API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Failed to fetch onecall data: {e}")
            return None
