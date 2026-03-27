"""
Satellite Layer: Google Earth Engine integration and NDVI processing
"""
from .gee_client import GEEClient, NDVITimeSeries
from .ndvi_processor import NDVIProcessor

__all__ = [
    "GEEClient",
    "NDVITimeSeries",
    "NDVIProcessor"
]
