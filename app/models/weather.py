from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WeatherData(BaseModel):
    location_id: str
    temperature: float
    humidity: float
    condition: str
    timestamp: datetime
    wind_speed: float
    pressure: float


class WeatherAlert(BaseModel):
    location_id: str
    condition_type: str
    threshold: float
    user_email: str
