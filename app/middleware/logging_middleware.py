from fastapi import Request, status
import logging
import time
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint
from uuid import uuid4

logger = logging.getLogger(__name__)

async def logging_middleware(
    request: Request,
    call_next: RequestResponseEndpoint
):
    request_id = str(uuid4())
    start_time = time.time()
    
    # Add request_id to request state
    request.state.request_id = request_id
    
    # Log request start
    logger.info(
        f"Request started | ID: {request_id} | Method: {request.method} | "
        f"Path: {request.url.path}"
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.3f}s"
        
        # Log successful response
        logger.info(
            f"Request completed | ID: {request_id} | Status: {response.status_code} | "
            f"Duration: {process_time:.3f}s"
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed | ID: {request_id} | Error: {str(e)} | "
            f"Duration: {process_time:.3f}s"
        )
        
        # Let the error middleware handle the exception
        # but add headers to the request state for later use
        request.state.headers = {
            "X-Request-ID": request_id,
            "X-Process-Time": f"{process_time:.3f}s"
        }
        raise