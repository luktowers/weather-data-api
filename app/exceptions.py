class WeatherAPIException(Exception):
    """Custom exception for Weather API related errors"""

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class WeatherAPIError(Exception):
    """Base exception for Weather API errors"""
    pass

class WeatherNotFoundError(WeatherAPIError):
    """Raised when weather data is not found"""
    pass

class WeatherServiceError(WeatherAPIError):
    """Raised when there's an error in the weather service"""
    pass