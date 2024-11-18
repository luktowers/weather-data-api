from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.exceptions import WeatherAPIError, WeatherNotFoundError
import logging
from starlette.middleware.base import RequestResponseEndpoint

logger = logging.getLogger(__name__)

async def error_handling_middleware(
    request: Request,
    call_next: RequestResponseEndpoint
):
    try:
        response = await call_next(request)
        return response
        
    except WeatherNotFoundError as e:
        logger.warning(f"Weather data not found: {str(e)}")
        response = JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(e)}
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )
        
    except WeatherAPIError as e:
        logger.error(f"Weather API error: {str(e)}")
        response = JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Weather service temporarily unavailable"}
        )
        
    except Exception as e:
        logger.exception("Unhandled exception: %s", str(e))
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"}
        )

    # Add headers from request state if they exist
    if hasattr(request.state, 'headers'):
        for key, value in request.state.headers.items():
            response.headers[key] = value
            
    return response