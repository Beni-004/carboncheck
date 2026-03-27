"""
DEPRECATED: Google Earth Engine client - Now redirects to Sentinel Hub.
This file is maintained for backward compatibility only.
All functionality has been migrated to sentinel_client.py

Use: from app.verification_engine.satellite_layer.sentinel_client import SentinelClient
Instead of: from app.verification_engine.satellite_layer.gee_client import GEEClient
"""

import warnings
import logging

# Issue deprecation warning
warnings.warn(
    "gee_client is deprecated. Use sentinel_client instead. "
    "GEEClient is now an alias for SentinelClient.",
    DeprecationWarning,
    stacklevel=2
)

logger = logging.getLogger(__name__)
logger.warning("gee_client.py is deprecated - importing from sentinel_client.py")

# Re-export everything from sentinel_client for backward compatibility
from app.verification_engine.satellite_layer.sentinel_client import (
    SentinelClient as GEEClient,
    SentinelClient,
    NDVITimeSeries,
    NDVIResult,
    get_ndvi
)

# Flag for checking availability (always True now - no GEE dependency)
GEE_AVAILABLE = False  # GEE is no longer used
SENTINEL_AVAILABLE = True

__all__ = [
    "GEEClient",  # Alias for backward compatibility
    "SentinelClient",
    "NDVITimeSeries",
    "NDVIResult",
    "get_ndvi",
    "GEE_AVAILABLE",
    "SENTINEL_AVAILABLE"
]
