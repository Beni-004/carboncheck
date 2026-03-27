"""
Main fraud scoring logic.
Compares ground truth vs satellite vs AI predictions.
"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FraudCheck(BaseModel):
    """Individual fraud check result."""
    name: str
    passed: bool
    score: int  # Points awarded (0-25)
    evidence: str
    severity: str  # "low", "medium", "high", "critical"


class TrustScoreResult(BaseModel):
    """Final verification result."""
    project_id: str
    trust_score: int  # 0-100
    verdict: str  # "PASS", "WARNING", "FAIL", "UNVERIFIED"
    checks: List[FraudCheck]
    
    # Evidence
    claimed_co2: float
    predicted_co2: float
    ndvi_avg: float
    ndvi_trend: float
    
    verified_at: datetime = Field(default_factory=datetime.utcnow)


class FraudScorer:
    """Calculate trust score from all verification layers."""
    
    def calculate_trust_score(
        self,
        ground_data,
        satellite_data: List,
        ai_prediction
    ) -> TrustScoreResult:
        """
        Main scoring function.
        
        Replaces old scoring logic with real verification.
        """
        from ..satellite_layer.ndvi_processor import NDVIProcessor
        from ..ai_layer.anomaly_detector import FraudAnomalyDetector
        
        checks = []
        
        # Extract key metrics
        claimed_co2 = ground_data.claimed_co2_tons
        predicted_co2 = ai_prediction.co2_tons
        
        processor = NDVIProcessor()
        ndvi_avg = processor.calculate_average(satellite_data)
        ndvi_trend = processor.calculate_trend(satellite_data)
        
        # CHECK 1: Carbon Overcrediting
        if predicted_co2 > 0:
            overcredit_ratio = claimed_co2 / predicted_co2
        else:
            overcredit_ratio = 999
        
        if overcredit_ratio < 1.5:
            check1 = FraudCheck(
                name="Carbon Overcrediting",
                passed=True,
                score=25,
                evidence=f"Claimed {claimed_co2:,.0f}t vs Predicted {predicted_co2:,.0f}t (ratio: {overcredit_ratio:.2f}x)",
                severity="low"
            )
        elif overcredit_ratio < 2.0:
            check1 = FraudCheck(
                name="Carbon Overcrediting",
                passed=False,
                score=15,
                evidence=f"Claimed {claimed_co2:,.0f}t vs Predicted {predicted_co2:,.0f}t (ratio: {overcredit_ratio:.2f}x) - Moderate overcrediting",
                severity="medium"
            )
        else:
            check1 = FraudCheck(
                name="Carbon Overcrediting",
                passed=False,
                score=0,
                evidence=f"Claimed {claimed_co2:,.0f}t vs Predicted {predicted_co2:,.0f}t (ratio: {overcredit_ratio:.2f}x) - Severe overcrediting",
                severity="high"
            )
        
        checks.append(check1)
        
        # CHECK 2: Vegetation Health (NDVI Trend)
        if ground_data.project_type in ["forestry", "afforestation"]:
            if ndvi_trend > 0.01:
                check2 = FraudCheck(
                    name="Vegetation Health",
                    passed=True,
                    score=25,
                    evidence=f"NDVI trend: +{ndvi_trend:.4f}/year (healthy growth)",
                    severity="low"
                )
            elif ndvi_trend > -0.01:
                check2 = FraudCheck(
                    name="Vegetation Health",
                    passed=False,
                    score=15,
                    evidence=f"NDVI trend: {ndvi_trend:+.4f}/year (stagnant growth)",
                    severity="medium"
                )
            else:
                check2 = FraudCheck(
                    name="Vegetation Health",
                    passed=False,
                    score=0,
                    evidence=f"NDVI trend: {ndvi_trend:+.4f}/year (vegetation loss detected)",
                    severity="high"
                )
        else:
            check2 = FraudCheck(
                name="Vegetation Health",
                passed=ndvi_trend > -0.02,
                score=25 if ndvi_trend > -0.02 else 10,
                evidence=f"NDVI trend: {ndvi_trend:+.4f}/year",
                severity="low" if ndvi_trend > -0.02 else "medium"
            )
        
        checks.append(check2)
        
        # CHECK 3: NDVI Baseline
        if ndvi_avg > 0.5:
            check3 = FraudCheck(
                name="Vegetation Baseline",
                passed=True,
                score=25,
                evidence=f"NDVI average: {ndvi_avg:.2f} (dense vegetation)",
                severity="low"
            )
        elif ndvi_avg > 0.3:
            check3 = FraudCheck(
                name="Vegetation Baseline",
                passed=True,
                score=20,
                evidence=f"NDVI average: {ndvi_avg:.2f} (moderate vegetation)",
                severity="low"
            )
        else:
            check3 = FraudCheck(
                name="Vegetation Baseline",
                passed=False,
                score=5,
                evidence=f"NDVI average: {ndvi_avg:.2f} (sparse vegetation - verify project type)",
                severity="medium"
            )
        
        checks.append(check3)
        
        # CHECK 4: Statistical Anomaly
        detector = FraudAnomalyDetector()
        
        features = {
            'overcredit_ratio': overcredit_ratio,
            'ndvi_avg': ndvi_avg,
            'ndvi_trend': ndvi_trend,
            'uncertainty': ai_prediction.uncertainty_pct / 100
        }
        
        is_anomaly = detector.predict(features)
        anomaly_score = detector.anomaly_score(features)
        
        if not is_anomaly:
            check4 = FraudCheck(
                name="Statistical Anomaly",
                passed=True,
                score=25,
                evidence=f"ML anomaly score: {anomaly_score:.2f} (normal pattern)",
                severity="low"
            )
        else:
            check4 = FraudCheck(
                name="Statistical Anomaly",
                passed=False,
                score=0,
                evidence=f"ML anomaly score: {anomaly_score:.2f} (unusual pattern detected)",
                severity="high"
            )
        
        checks.append(check4)
        
        # CALCULATE FINAL SCORE
        total_score = sum(check.score for check in checks)
        
        # DETERMINE VERDICT
        if total_score >= 70:
            verdict = "PASS"
        elif total_score >= 40:
            verdict = "WARNING"
        else:
            verdict = "FAIL"
        
        return TrustScoreResult(
            project_id=ground_data.project_id,
            trust_score=total_score,
            verdict=verdict,
            checks=checks,
            claimed_co2=claimed_co2,
            predicted_co2=predicted_co2,
            ndvi_avg=ndvi_avg,
            ndvi_trend=ndvi_trend
        )
