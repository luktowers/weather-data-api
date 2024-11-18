class WeatherAPIException(Exception):
    """Custom exception for Weather API related errors"""

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
