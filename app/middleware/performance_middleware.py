from fastapi import Request
import logging
import time
from starlette.middleware.base import RequestResponseEndpoint

logger = logging.getLogger(__name__)
SLOW_REQUEST_THRESHOLD = 0.5  # Lower threshold for testing

async def performance_middleware(
    request: Request,
    call_next: RequestResponseEndpoint
):
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        response.headers["X-Response-Time"] = f"{process_time:.3f}s"
        
        if process_time > SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"Very slow request detected | Method: {request.method} | "  # Changed "Slow" to "Very slow"
                f"Path: {request.url.path} | Duration: {process_time:.3f}s"
            )
        
        return response
        
    except Exception:
        process_time = time.time() - start_time
        request.state.response_time = f"{process_time:.3f}s"
        raise