from fastapi import APIRouter, HTTPException, Query
from app.services.weather_service import WeatherService
from app.services.cache_service import WeatherCache
from app.services.storage_service import StorageService
from typing import Optional

router = APIRouter()
weather_service = WeatherService()
weather_cache = WeatherCache()
storage_service = StorageService()


@router.get("/forecast/coordinates")
async def get_weather_forecast(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    units: str = Query(
        "metric", description="Units of measurement (metric, imperial, standard)"
    ),
    exclude: Optional[str] = Query(
        None, description="Parts to exclude (current,minutely,hourly,daily,alerts)"
    ),
):
    """Get current weather and forecast data using OneCall API 3.0"""
    # Check cache first
    cache_key = f"onecall_{lat}_{lon}_{units}"
    cached_data = weather_cache.get(cache_key)
    if cached_data:
        return cached_data

    # Check persistent storage
    stored_data = await storage_service.get_forecast(lat, lon, units)
    if stored_data:
        # Update cache and return stored data
        weather_cache.set(cache_key, stored_data)
        return stored_data

    # Prepare parameters for API call
    api_params = {
        "lat": lat,
        "lon": lon,
        "units": units,
        "api_key": weather_service.api_key,
    }

    # Only add exclude if it's not None
    if exclude is not None:
        api_params["exclude"] = exclude

    # Fetch fresh data if not in cache or storage
    forecast_data = await weather_service.fetch_onecall_data(**api_params)

    if not forecast_data:
        raise HTTPException(status_code=404, detail="Weather forecast data not found")

    # Store in both cache and persistent storage
    weather_cache.set(cache_key, forecast_data)
    await storage_service.store_forecast(lat, lon, units, forecast_data)

    return forecast_data
