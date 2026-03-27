"""
Process NDVI time series data.
Calculate trends, detect anomalies.
"""
import numpy as np
from scipy import stats
from typing import List, Tuple
from datetime import datetime
from .sentinel_client import NDVITimeSeries


class NDVIProcessor:
    """Analyze NDVI time series for vegetation trends."""
    
    def calculate_trend(self, timeseries: List[NDVITimeSeries]) -> float:
        """
        Calculate NDVI trend (slope over time).
        
        Positive slope = vegetation increasing
        Negative slope = vegetation decreasing
        
        Returns:
            Slope in NDVI units per year
        """
        if len(timeseries) < 2:
            return 0.0
        
        # Convert dates to ordinal for regression
        x = np.array([t.date.toordinal() for t in timeseries])
        y = np.array([t.ndvi for t in timeseries])
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Convert slope to per-year (x is in days)
        slope_per_year = slope * 365.25
        
        return float(slope_per_year)
    
    def calculate_average(self, timeseries: List[NDVITimeSeries]) -> float:
        """Calculate mean NDVI over time period."""
        if not timeseries:
            return 0.0
        
        return float(np.mean([t.ndvi for t in timeseries]))
    
    def detect_anomalies(
        self,
        timeseries: List[NDVITimeSeries],
        threshold_std: float = 2.0
    ) -> List[NDVITimeSeries]:
        """
        Detect anomalous NDVI values (sudden drops/spikes).
        
        Args:
            timeseries: NDVI observations
            threshold_std: Standard deviations from mean to flag
        
        Returns:
            List of anomalous observations
        """
        if len(timeseries) < 3:
            return []
        
        values = np.array([t.ndvi for t in timeseries])
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return []
        
        anomalies = []
        for t in timeseries:
            z_score = abs(t.ndvi - mean) / std
            if z_score > threshold_std:
                anomalies.append(t)
        
        return anomalies
    
    def segment_trend(
        self,
        timeseries: List[NDVITimeSeries]
    ) -> List[Tuple[datetime, datetime, float]]:
        """
        Segment time series into periods of different trends.
        Useful for detecting deforestation events.
        
        Returns:
            List of (start_date, end_date, slope) tuples
        """
        if len(timeseries) < 2:
            return []
        
        slope = self.calculate_trend(timeseries)
        return [(timeseries[0].date, timeseries[-1].date, slope)]
