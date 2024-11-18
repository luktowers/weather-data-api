import logging
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.middleware.logging_middleware import logging_middleware
from app.middleware.error_middleware import error_handling_middleware
from app.middleware.performance_middleware import performance_middleware
from app.exceptions import WeatherNotFoundError, WeatherAPIError

@pytest.fixture
def test_app():
    app = FastAPI()
    # Order matters: logging first, then error handling, then performance
    app.middleware("http")(logging_middleware)
    app.middleware("http")(error_handling_middleware)
    app.middleware("http")(performance_middleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}
        
    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")
    
    @app.get("/weather-not-found")
    async def weather_not_found():
        raise WeatherNotFoundError("Weather data not found")
    
    @app.get("/weather-api-error")
    async def weather_api_error():
        raise WeatherAPIError("Weather API error")
    
    @app.get("/slow")
    async def slow_endpoint():
        import asyncio
        await asyncio.sleep(2)
        return {"message": "slow response"}
    
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

class TestLoggingMiddleware:
    def test_successful_request_logging(self, client, caplog):
        caplog.set_level(logging.INFO)
        
        response = client.get("/test")
        
        assert response.status_code == 200
        assert any("Request started" in record.message for record in caplog.records)
        assert any("Request completed" in record.message for record in caplog.records)
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers

    def test_failed_request_logging(self, client, caplog):
        with caplog.at_level(logging.INFO):  # Change to INFO to capture all logs
            response = client.get("/error")
        
        assert response.status_code == 500
        assert any("Request started" in record.message for record in caplog.records)
        assert any("Request failed" in record.message for record in caplog.records)


class TestErrorHandlingMiddleware:
    def test_weather_not_found_error(self, client):
        response = client.get("/weather-not-found")
        
        assert response.status_code == 404
        assert response.json() == {"detail": "Weather data not found"}

    def test_weather_api_error(self, client):
        response = client.get("/weather-api-error")
        
        assert response.status_code == 503
        assert response.json() == {"detail": "Weather service temporarily unavailable"}

    def test_unhandled_error(self, client):
        response = client.get("/error")
        
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}

class TestPerformanceMiddleware:
    def test_response_time_header(self, client):
        response = client.get("/test")
        
        assert "X-Response-Time" in response.headers
        assert response.headers["X-Response-Time"].endswith("s")

    @patch("app.middleware.performance_middleware.logger")
    def test_slow_request_logging(self, mock_logger, client):
        response = client.get("/slow")
        
        assert response.status_code == 200
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "Very slow request detected" in warning_message

class TestMiddlewareIntegration:
    def test_middleware_order(self, client):
        response = client.get("/test")
        
        headers = response.headers
        assert all(key in headers for key in [
            "X-Request-ID",
            "X-Process-Time",
            "X-Response-Time"
        ])

    def test_error_with_all_middleware(self, client, caplog):
        with caplog.at_level(logging.INFO):  # Change from ERROR to INFO level
            response = client.get("/error")
        
            assert response.status_code == 500
            # Check for both start and completion log messages
            assert any("Request started" in record.message for record in caplog.records)
            assert any("Request failed" in record.message for record in caplog.records)
            assert "X-Request-ID" in response.headers
            assert "X-Response-Time" in response.headers

    @patch("app.middleware.logging_middleware.logger")
    @patch("app.middleware.performance_middleware.logger")
    def test_slow_request_with_all_middleware(
        self, mock_perf_logger, mock_log_logger, client
    ):
        response = client.get("/slow")
        
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers
        assert "X-Response-Time" in response.headers
        
        # Verify logging
        mock_log_logger.info.assert_called()
        mock_perf_logger.warning.assert_called_once()