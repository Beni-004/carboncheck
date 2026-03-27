"""
Error Mapping Middleware.
Ensures no HTTP 500 errors are returned for business logic failures.
Maps exceptions to appropriate 4xx or 503 responses.
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Union

logger = logging.getLogger(__name__)


class BusinessError(Exception):
    """Base class for expected business logic errors."""

    def __init__(self, message: str, status_code: int = 400, error_code: str = "BUSINESS_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class ValidationError(BusinessError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")


class NotFoundError(BusinessError):
    """Raised when a resource is not found."""

    def __init__(self, message: str):
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class ServiceDegradedError(BusinessError):
    """Raised when service is degraded but still functional."""

    def __init__(self, message: str):
        super().__init__(message, status_code=503, error_code="SERVICE_DEGRADED")


class RateLimitError(BusinessError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT_EXCEEDED")


async def error_mapping_middleware(request: Request, call_next):
    """
    Middleware that catches exceptions and maps them to appropriate HTTP responses.

    Business logic errors -> 4xx/503
    Unexpected errors -> Still 503, never 500

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        JSONResponse with appropriate status code
    """
    try:
        response = await call_next(request)
        return response

    except BusinessError as e:
        # Expected business errors
        logger.warning(
            f"Business error on {request.method} {request.url.path}: "
            f"{e.error_code} - {e.message}"
        )

        return JSONResponse(
            status_code=e.status_code,
            content={
                "error_code": e.error_code,
                "error_message": e.message,
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path)
            }
        )

    except Exception as e:
        # Unexpected errors - return 503 instead of 500
        logger.error(
            f"Unexpected error on {request.method} {request.url.path}: {e}",
            exc_info=True
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error_code": "SERVICE_UNAVAILABLE",
                "error_message": "Service temporarily unavailable. Please try again later.",
                "details": {
                    "exception_type": type(e).__name__,
                    "path": str(request.url.path)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        )


def create_error_response(
    error_code: str,
    error_message: str,
    status_code: int = 400,
    details: Union[dict, None] = None
) -> JSONResponse:
    """
    Helper to create standardized error responses.

    Args:
        error_code: Machine-readable error code
        error_message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional context

    Returns:
        JSONResponse with error payload
    """
    content = {
        "error_code": error_code,
        "error_message": error_message,
        "timestamp": datetime.utcnow().isoformat()
    }

    if details:
        content["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=content
    )
