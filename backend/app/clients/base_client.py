"""
Base client with timeout and fallback handling.
Ensures all upstream API calls respect the 3-second timeout constraint.
"""

import httpx
import asyncio
import logging
from typing import Optional, Any, Callable, TypeVar
from datetime import datetime
from app.scoring.constants import EXTERNAL_API_TIMEOUT

logger = logging.getLogger(__name__)

T = TypeVar('T')

# Global pooled HTTP client - reused across all requests
_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    """Get or create a pooled HTTP client instance."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=EXTERNAL_API_TIMEOUT)
    return _http_client


async def close_http_client() -> None:
    """Close the global HTTP client (call during app shutdown)."""
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


class TimeoutError(Exception):
    """Raised when an API call exceeds the timeout limit."""
    pass


class UpstreamAPIError(Exception):
    """Raised when an upstream API returns an error."""
    pass


async def call_with_timeout(
    func: Callable[..., Any],
    *args,
    timeout: float = EXTERNAL_API_TIMEOUT,
    fallback: Optional[Any] = None,
    source_name: str = "unknown",
    **kwargs
) -> tuple[Any, bool]:
    """
    Execute an async function with strict timeout enforcement.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        timeout: Maximum execution time in seconds
        fallback: Value to return on timeout/error (None = raise)
        source_name: Name of the source for logging
        **kwargs: Keyword arguments for func

    Returns:
        Tuple of (result, used_fallback)
        - result: Function result or fallback value
        - used_fallback: True if fallback was used, False if live data

    Raises:
        TimeoutError: If timeout exceeded and no fallback provided
        UpstreamAPIError: If function raises and no fallback provided
    """
    start_time = datetime.now()

    try:
        # Execute with timeout
        result = await asyncio.wait_for(
            func(*args, **kwargs),
            timeout=timeout
        )

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"[{source_name}] Success in {elapsed:.2f}s")

        return result, False

    except asyncio.TimeoutError:
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.warning(f"[{source_name}] Timeout after {elapsed:.2f}s (limit: {timeout}s)")

        if fallback is not None:
            logger.info(f"[{source_name}] Using fallback data")
            return fallback, True
        else:
            raise TimeoutError(f"{source_name} exceeded {timeout}s timeout")

    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.error(f"[{source_name}] Error after {elapsed:.2f}s: {e}")

        if fallback is not None:
            logger.info(f"[{source_name}] Using fallback data due to error")
            return fallback, True
        else:
            raise UpstreamAPIError(f"{source_name} error: {str(e)}") from e


async def http_get_with_timeout(
    url: str,
    timeout: float = EXTERNAL_API_TIMEOUT,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    fallback: Optional[Any] = None,
    source_name: str = "http"
) -> tuple[Optional[httpx.Response], bool]:
    """
    Perform HTTP GET with timeout and fallback handling using pooled client.

    Args:
        url: Target URL
        timeout: Request timeout in seconds
        headers: Optional HTTP headers
        params: Optional query parameters
        fallback: Value to return on timeout/error
        source_name: Name for logging

    Returns:
        Tuple of (response, used_fallback)
    """
    async def make_request():
        client = get_http_client()  # Use pooled client
        response = await client.get(
            url,
            headers=headers,
            params=params,
            timeout=timeout
        )
        response.raise_for_status()
        return response

    return await call_with_timeout(
        make_request,
        timeout=timeout,
        fallback=fallback,
        source_name=source_name
    )


async def http_post_with_timeout(
    url: str,
    json: Optional[dict] = None,
    data: Optional[Any] = None,
    timeout: float = EXTERNAL_API_TIMEOUT,
    headers: Optional[dict] = None,
    fallback: Optional[Any] = None,
    source_name: str = "http"
) -> tuple[Optional[httpx.Response], bool]:
    """
    Perform HTTP POST with timeout and fallback handling using pooled client.

    Args:
        url: Target URL
        json: JSON payload
        data: Form data payload
        timeout: Request timeout in seconds
        headers: Optional HTTP headers
        fallback: Value to return on timeout/error
        source_name: Name for logging

    Returns:
        Tuple of (response, used_fallback)
    """
    async def make_request():
        client = get_http_client()  # Use pooled client
        response = await client.post(
            url,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response

    return await call_with_timeout(
        make_request,
        timeout=timeout,
        fallback=fallback,
        source_name=source_name
    )
