"""
Request/Response logging middleware.
"""

import time
import json
from fastapi import Request
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def log_request_middleware(request: Request, call_next):
    """Log all incoming requests and outgoing responses."""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Error: {request.method} {request.url.path} - "
            f"Error: {str(e)} - Time: {process_time:.3f}s"
        )
        raise


def setup_logging_middleware(app):
    """Add request/response logging middleware."""
    app.middleware("http")(log_request_middleware)
