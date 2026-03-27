"""
Detect statistical anomalies in carbon projects.
Uses: scikit-learn Isolation Forest
Reference: https://github.com/yzhao062/pyod
"""
from sklearn.ensemble import IsolationForest
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class FraudAnomalyDetector:
    """
    Detect fraudulent projects using anomaly detection.
    
    Flags projects with unusual patterns:
    - Overcrediting (claimed >> predicted)
    - Low NDVI with high carbon claims
    - Unusual NDVI trends
    """
    
    def __init__(self):
        """Initialize with pre-trained model or train on historical data."""
        self.model = IsolationForest(
            contamination=0.1,  # Expect 10% of projects to be fraudulent
            random_state=42
        )
        
        # Train on synthetic data for demo
        self._train_on_synthetic_data()
    
    def _train_on_synthetic_data(self):
        """Train on synthetic historical data for demo purposes."""
        # Generate synthetic training data
        # Normal projects: overcredit_ratio ~1.0, ndvi_avg ~0.6, ndvi_trend ~0.01
        normal_data = np.random.normal(
            loc=[1.0, 0.6, 0.01, 0.3],
            scale=[0.2, 0.1, 0.01, 0.05],
            size=(100, 4)
        )
        
        # Anomalous projects: high overcredit, low ndvi
        anomalous_data = np.random.normal(
            loc=[2.5, 0.3, -0.02, 0.5],
            scale=[0.5, 0.1, 0.01, 0.1],
            size=(10, 4)
        )
        
        training_data = np.vstack([normal_data, anomalous_data])
        self.model.fit(training_data)
        logger.info("Fraud detector trained on synthetic data")
    
    def train(self, training_data: np.ndarray):
        """
        Train on historical data.
        
        Args:
            training_data: Array of shape (n_samples, n_features)
                Features: [claimed_co2, predicted_co2, ndvi_avg, ndvi_trend, ...]
        """
        self.model.fit(training_data)
    
    def predict(self, features: Dict[str, float]) -> bool:
        """
        Detect if project shows anomalous patterns.
        
        Args:
            features: Dictionary with:
                - overcredit_ratio: claimed / predicted
                - ndvi_avg: Average NDVI
                - ndvi_trend: NDVI slope per year
                - uncertainty: Uncertainty in prediction
        
        Returns:
            True if anomalous (likely fraud), False if normal
        """
        # Convert features to array
        feature_array = np.array([[
            features['overcredit_ratio'],
            features['ndvi_avg'],
            features['ndvi_trend'],
            features['uncertainty']
        ]])
        
        # Predict: -1 = anomaly, 1 = normal
        prediction = self.model.predict(feature_array)[0]
        
        return prediction == -1
    
    def anomaly_score(self, features: Dict[str, float]) -> float:
        """
        Get anomaly score (0-1, higher = more anomalous).
        
        Returns:
            Anomaly score between 0 (normal) and 1 (extreme anomaly)
        """
        feature_array = np.array([[
            features['overcredit_ratio'],
            features['ndvi_avg'],
            features['ndvi_trend'],
            features['uncertainty']
        ]])
        
        # Get anomaly score
        score = self.model.decision_function(feature_array)[0]
        
        # Normalize to 0-1 range
        normalized_score = 1 / (1 + np.exp(score))
        
        return float(normalized_score)
