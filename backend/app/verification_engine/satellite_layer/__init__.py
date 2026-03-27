"""
Satellite Layer: Sentinel Hub integration and NDVI processing.
Fetches vegetation data from Copernicus Sentinel-2 satellite imagery.

NOTE: Google Earth Engine (GEE) has been replaced with Sentinel Hub API.
The GEEClient class is now an alias for SentinelClient for backward compatibility.
"""
from .sentinel_client import SentinelClient, NDVITimeSeries, NDVIResult, get_ndvi
from .ndvi_processor import NDVIProcessor

# Backward compatibility alias
GEEClient = SentinelClient

__all__ = [
    "SentinelClient",
    "GEEClient",  # Deprecated alias for SentinelClient
    "NDVITimeSeries",
    "NDVIResult",
    "NDVIProcessor",
    "get_ndvi"
]
