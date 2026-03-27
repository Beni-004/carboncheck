"""
Google Earth Engine client for satellite data retrieval.
Based on: google/earthengine-api
"""
import logging
from datetime import datetime
from typing import List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Conditionally import Earth Engine
try:
    import ee
    GEE_AVAILABLE = True
except ImportError:
    GEE_AVAILABLE = False
    logger.warning("Google Earth Engine not available - using mock data")


class NDVITimeSeries(BaseModel):
    """Time series of NDVI values."""
    date: datetime
    ndvi: float
    cloud_cover: float


class GEEClient:
    """
    Client for querying Google Earth Engine.
    
    Uses Sentinel-2 for NDVI calculation.
    Reference: https://github.com/google/earthengine-api
    """
    
    def __init__(self):
        """Initialize Earth Engine."""
        self.initialized = False
        
        if GEE_AVAILABLE:
            try:
                ee.Initialize()
                self.initialized = True
                logger.info("Google Earth Engine initialized successfully")
            except Exception as e:
                logger.warning(f"GEE initialization failed: {e}")
                logger.warning("Falling back to mock NDVI data")
        else:
            logger.warning("GEE not available, using mock data")
    
    def get_ndvi_timeseries(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
        buffer_m: int = 1000
    ) -> List[NDVITimeSeries]:
        """
        Fetch NDVI time series for a location.
        
        Args:
            lat: Latitude
            lon: Longitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            buffer_m: Buffer radius around point
        
        Returns:
            List of NDVI observations
        """
        if self.initialized:
            return self._fetch_real_ndvi(lat, lon, start_date, end_date, buffer_m)
        else:
            return self._generate_mock_ndvi(lat, lon, start_date, end_date)
    
    def _fetch_real_ndvi(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
        buffer_m: int
    ) -> List[NDVITimeSeries]:
        """Fetch real NDVI data from Google Earth Engine."""
        try:
            # Create point geometry
            point = ee.Geometry.Point([lon, lat])
            roi = point.buffer(buffer_m)
            
            # Load Sentinel-2 Surface Reflectance
            sentinel = ee.ImageCollection('COPERNICUS/S2_SR') \
                .filterBounds(roi) \
                .filterDate(start_date, end_date) \
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
            
            # Function to calculate NDVI
            def add_ndvi(image):
                ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
                return image.addBands(ndvi)
            
            ndvi_collection = sentinel.map(add_ndvi)
            
            # Extract time series
            def extract_value(image):
                stats = image.select('NDVI').reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=roi,
                    scale=10
                )
                
                return ee.Feature(None, {
                    'date': image.date().format('YYYY-MM-dd'),
                    'ndvi': stats.get('NDVI'),
                    'cloud_cover': image.get('CLOUDY_PIXEL_PERCENTAGE')
                })
            
            features = ndvi_collection.map(extract_value)
            data = features.getInfo()
            
            # Parse into Pydantic models
            results = []
            for feature in data['features']:
                props = feature['properties']
                
                if props['ndvi'] is not None:
                    results.append(NDVITimeSeries(
                        date=datetime.strptime(props['date'], '%Y-%m-%d'),
                        ndvi=float(props['ndvi']),
                        cloud_cover=float(props['cloud_cover'])
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error fetching real NDVI: {e}")
            return self._generate_mock_ndvi(lat, lon, start_date, end_date)
    
    def _generate_mock_ndvi(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str
    ) -> List[NDVITimeSeries]:
        """Generate mock NDVI data for testing."""
        import numpy as np
        from datetime import timedelta
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate monthly observations
        results = []
        current = start
        base_ndvi = 0.65
        
        while current <= end:
            # Add some seasonal variation
            month_factor = np.sin((current.month / 12) * 2 * np.pi) * 0.1
            noise = np.random.normal(0, 0.05)
            ndvi = base_ndvi + month_factor + noise
            ndvi = max(0.0, min(1.0, ndvi))
            
            results.append(NDVITimeSeries(
                date=current,
                ndvi=ndvi,
                cloud_cover=np.random.uniform(5, 15)
            ))
            
            current += timedelta(days=30)
        
        logger.info(f"Generated {len(results)} mock NDVI observations")
        return results
    
    def get_latest_ndvi(self, lat: float, lon: float) -> float:
        """Get most recent NDVI value for a location."""
        from datetime import timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        timeseries = self.get_ndvi_timeseries(
            lat, lon,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if timeseries:
            return timeseries[-1].ndvi
        return 0.65
