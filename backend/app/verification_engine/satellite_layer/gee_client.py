"""
Google Earth Engine client for satellite data retrieval.
Based on: google/earthengine-api
"""
import logging
import os
import hashlib
from datetime import datetime
from typing import List, Tuple, Optional
from pydantic import BaseModel
from app.clients.base_client import call_with_timeout
from app.services.cache_repository import CacheRepository
from app.scoring.constants import EXTERNAL_API_TIMEOUT

logger = logging.getLogger(__name__)

# Conditionally import Earth Engine
try:
    import ee
    GEE_AVAILABLE = True
except ImportError:
    GEE_AVAILABLE = False
    logger.warning("Google Earth Engine not available - using deterministic mock data")


class NDVITimeSeries(BaseModel):
    """Time series of NDVI values."""
    date: datetime
    ndvi: float
    cloud_cover: float


class GEEClient:
    """
    Client for querying Google Earth Engine with timeout and cache fallback.

    Uses Sentinel-2 for NDVI calculation.
    Reference: https://github.com/google/earthengine-api
    """

    def __init__(self):
        """Initialize Earth Engine with service account if available."""
        self.initialized = False
        self.cache = CacheRepository()

        if GEE_AVAILABLE:
            try:
                # Try service account authentication first
                credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                if credentials_path and os.path.exists(credentials_path):
                    credentials = ee.ServiceAccountCredentials(
                        email=None,  # Will be read from the JSON file
                        key_file=credentials_path
                    )
                    ee.Initialize(credentials=credentials)
                    self.initialized = True
                    logger.info("Google Earth Engine initialized with service account")
                else:
                    # Try default authentication
                    ee.Initialize()
                    self.initialized = True
                    logger.info("Google Earth Engine initialized with default credentials")
            except Exception as e:
                logger.warning(f"GEE initialization failed: {e}")
                logger.info("Using deterministic mock NDVI data based on project ID")
        else:
            logger.info("GEE not available, using deterministic mock data")
    
    async def get_ndvi_timeseries(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
        buffer_m: int = 1000,
        project_id: Optional[str] = None
    ) -> Tuple[List[NDVITimeSeries], bool]:
        """
        Fetch NDVI time series for a location with timeout and cache fallback.

        Args:
            lat: Latitude
            lon: Longitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            buffer_m: Buffer radius around point
            project_id: Project ID for caching

        Returns:
            Tuple of (List of NDVI observations, used_fallback: bool)
        """
        # Fetch cached data once (if project_id provided)
        cached_series = None
        if project_id:
            cached_data = await self.cache.get_cached_satellite_data(project_id)
            if cached_data:
                cached_series = [NDVITimeSeries(**item) for item in cached_data]

        try:
            async def fetch_live():
                if self.initialized:
                    return self._fetch_real_ndvi(lat, lon, start_date, end_date, buffer_m, project_id)
                else:
                    return self._generate_mock_ndvi(lat, lon, start_date, end_date, project_id)

            # Fetch with timeout using cached data as fallback
            ndvi_series, used_fallback = await call_with_timeout(
                fetch_live,
                timeout=EXTERNAL_API_TIMEOUT,
                fallback=cached_series or self._generate_mock_ndvi(lat, lon, start_date, end_date, project_id),
                source_name="Google-Earth-Engine"
            )

            # Save to cache if successful live fetch
            if ndvi_series and not used_fallback and project_id:
                await self.cache.save_satellite_data(
                    project_id,
                    [item.model_dump() for item in ndvi_series]
                )

            return ndvi_series, used_fallback

        except Exception as e:
            logger.error(f"Error fetching NDVI for ({lat}, {lon}): {e}")

            # Use already-fetched cached data (no second query)
            if cached_series:
                return cached_series, True

            # Final fallback to deterministic mock data
            return self._generate_mock_ndvi(lat, lon, start_date, end_date, project_id), True
    
    def _fetch_real_ndvi(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
        buffer_m: int,
        project_id: Optional[str] = None
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
            return self._generate_mock_ndvi(lat, lon, start_date, end_date, project_id)
    
    def _generate_mock_ndvi(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
        project_id: Optional[str] = None
    ) -> List[NDVITimeSeries]:
        """
        Generate deterministic mock NDVI data based on project ID.

        Different project IDs produce different but consistent NDVI profiles:
        - Some projects show healthy growth (high scores)
        - Some show stagnant/declining vegetation (low scores)
        - Results are reproducible for the same project ID
        """
        import numpy as np
        from datetime import timedelta

        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        # Create deterministic seed from project_id
        if project_id:
            seed = int(hashlib.md5(project_id.encode()).hexdigest()[:8], 16)
        else:
            seed = int(hashlib.md5(f"{lat}{lon}".encode()).hexdigest()[:8], 16)

        rng = np.random.RandomState(seed)

        # Determine project characteristics from seed
        # This creates variety: some projects healthy, some problematic
        project_hash = seed % 100

        if project_hash < 20:
            # 20% of projects: Excellent vegetation (high NDVI, positive trend)
            base_ndvi = 0.72 + rng.uniform(0, 0.08)
            trend_per_year = 0.015 + rng.uniform(0, 0.01)
            noise_scale = 0.03
        elif project_hash < 50:
            # 30% of projects: Good vegetation (moderate-high NDVI)
            base_ndvi = 0.58 + rng.uniform(0, 0.12)
            trend_per_year = 0.005 + rng.uniform(-0.005, 0.01)
            noise_scale = 0.05
        elif project_hash < 75:
            # 25% of projects: Moderate vegetation (concerning trend)
            base_ndvi = 0.45 + rng.uniform(0, 0.15)
            trend_per_year = rng.uniform(-0.01, 0.005)
            noise_scale = 0.06
        else:
            # 25% of projects: Poor/declining vegetation (low scores)
            base_ndvi = 0.25 + rng.uniform(0, 0.20)
            trend_per_year = -0.02 + rng.uniform(-0.01, 0.005)
            noise_scale = 0.08

        # Generate monthly observations
        results = []
        current = start
        months_elapsed = 0

        while current <= end:
            # Calculate NDVI with trend, seasonal variation, and noise
            years_elapsed = months_elapsed / 12.0
            trend_effect = trend_per_year * years_elapsed

            # Seasonal variation (higher in summer)
            seasonal = np.sin((current.month / 12) * 2 * np.pi - np.pi/2) * 0.08

            # Deterministic noise based on date
            date_seed = seed + current.year * 1000 + current.month
            date_rng = np.random.RandomState(date_seed)
            noise = date_rng.normal(0, noise_scale)

            ndvi = base_ndvi + trend_effect + seasonal + noise
            ndvi = max(0.05, min(0.95, ndvi))  # Clamp to valid range

            results.append(NDVITimeSeries(
                date=current,
                ndvi=ndvi,
                cloud_cover=date_rng.uniform(5, 20)
            ))

            current += timedelta(days=30)
            months_elapsed += 1

        logger.info(f"Generated {len(results)} deterministic NDVI observations for {project_id or 'unknown'} (base={base_ndvi:.2f}, trend={trend_per_year:+.4f}/yr)")
        return results
    
    async def get_latest_ndvi(self, lat: float, lon: float) -> float:
        """Get most recent NDVI value for a location."""
        from datetime import timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        timeseries, _ = await self.get_ndvi_timeseries(
            lat, lon,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

        if timeseries:
            return timeseries[-1].ndvi
        return 0.65
