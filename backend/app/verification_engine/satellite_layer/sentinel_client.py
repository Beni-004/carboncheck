"""
Sentinel Hub client for satellite data retrieval.
Replaces Google Earth Engine (GEE) integration.
Reference: https://docs.sentinel-hub.com/api/latest/
"""

import logging
from typing import List, Tuple, Optional
from datetime import datetime
from pydantic import BaseModel

from app.services.satellite_service import (
    SentinelHubClient,
    NDVITimeSeries,
    NDVIResult,
    get_ndvi as fetch_ndvi_from_sentinel
)

logger = logging.getLogger(__name__)

# Re-export for backward compatibility
__all__ = [
    "SentinelClient",
    "NDVITimeSeries",
    "NDVIResult",
    "get_ndvi"
]


class SentinelClient(SentinelHubClient):
    """
    Client for Sentinel Hub API (replaces GEEClient).

    Uses Sentinel-2 L2A for NDVI calculation.
    Reference: https://docs.sentinel-hub.com/api/latest/
    """

    def __init__(self):
        """Initialize Sentinel Hub client with OAuth credentials."""
        super().__init__()
        logger.info("SentinelClient initialized (Sentinel Hub API)")


# Alias for backward compatibility with verify_service.py
GEEClient = SentinelClient


async def get_ndvi(
    bbox: List[float],
    start_date: str,
    end_date: str,
    max_cloud_cover: int = 20
) -> dict:
    """
    Fetch NDVI data from Sentinel-2 (convenience wrapper).

    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        max_cloud_cover: Maximum cloud cover percentage

    Returns:
        Dict with ndvi_mean, ndvi_values, timestamp, data_source
    """
    return await fetch_ndvi_from_sentinel(bbox, start_date, end_date, max_cloud_cover)
