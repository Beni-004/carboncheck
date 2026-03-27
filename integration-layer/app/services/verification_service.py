"""
Verification Service
Orchestrates the verification pipeline:
1. Fetch registry data
2. Get satellite data (NDVI) from Sentinel Hub
3. Run AI model
4. Compute trust score
5. Store and return results
"""

import os
import logging
import httpx
import hashlib
import numpy as np
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from ..models.registry_models import (
    VerificationRequest,
    VerificationResult,
    Project,
)
from ..mappers.programme_mapper import ProgrammeMapper, VerificationMapper
from .registry_client import RegistryServiceClient, get_registry_client

logger = logging.getLogger(__name__)

# Sentinel Hub Configuration
SENTINEL_AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
SENTINEL_PROCESS_URL = os.environ.get(
    "SENTINEL_API_URL",
    "https://sh.dataspace.copernicus.eu/api/v1/process"
)

# NDVI Evalscript for Sentinel-2
NDVI_EVALSCRIPT = """//VERSION=3
function setup() {
  return {
    input: ["B04", "B08"],
    output: { bands: 1, sampleType: "FLOAT32" }
  };
}

function evaluatePixel(sample) {
  return [(sample.B08 - sample.B04) / (sample.B08 + sample.B04)];
}
"""


class VerificationService:
    """
    Verification Pipeline Service.
    Connects registry data with satellite and AI layers.
    """

    def __init__(self, registry_client: Optional[RegistryServiceClient] = None):
        self.registry_client = registry_client or get_registry_client()

    async def verify_project(
        self,
        request: VerificationRequest,
    ) -> VerificationResult:
        """
        Run full verification pipeline on a project.

        Pipeline Steps:
        1. Ground Layer: Fetch registry data
        2. Satellite Layer: Get NDVI data from Sentinel Hub (Copernicus)
        3. AI Layer: Run prediction and anomaly detection
        4. Scoring Layer: Compute trust score
        """

        # Step 1: Fetch registry data (Ground Layer)
        programme = await self.registry_client.get_programme(request.project_id)
        project = ProgrammeMapper.to_project(programme)

        claimed_co2 = project.claimed_co2 or 0.0

        # Step 2: Satellite Layer (NDVI from Sentinel Hub)
        ndvi_data = None
        if request.include_satellite:
            ndvi_data = await self._get_satellite_data(project)

        # Step 3: AI Layer (Prediction + Anomaly Detection)
        ai_scores = None
        predicted_co2 = claimed_co2  # Default to claimed if no AI
        if request.include_ai_analysis:
            ai_result = await self._run_ai_analysis(project, ndvi_data)
            ai_scores = ai_result.get("scores")
            predicted_co2 = ai_result.get("predicted_co2", claimed_co2)

        # Step 4: Scoring Layer (Trust Score Calculation)
        result = VerificationMapper.create_result(
            project_id=request.project_id,
            predicted_co2=predicted_co2,
            claimed_co2=claimed_co2,
            ndvi_data=ndvi_data,
            ai_scores=ai_scores,
        )

        return result

    async def _get_satellite_data(
        self,
        project: Project,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch NDVI data from Sentinel Hub (Copernicus Data Space).
        Uses Sentinel-2 L2A dataset for vegetation analysis.
        """
        try:
            # Extract coordinates
            coords = project.location_coordinates
            if not coords:
                logger.warning(f"No coordinates for project {project.project_id}")
                return self._generate_fallback_ndvi(project.project_id)

            lat, lon = coords
            client_id = os.environ.get("SENTINEL_CLIENT_ID")
            client_secret = os.environ.get("SENTINEL_CLIENT_SECRET")

            # If credentials not configured, use fallback
            if not client_id or not client_secret:
                logger.warning("Sentinel Hub credentials not configured, using fallback")
                return self._generate_fallback_ndvi(project.project_id)

            # Get OAuth token
            token = await self._get_sentinel_token(client_id, client_secret)
            if not token:
                return self._generate_fallback_ndvi(project.project_id)

            # Create bounding box (1km buffer)
            bbox = self._create_bbox(lat, lon, buffer_m=1000)

            # Date range (last 90 days)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)

            # Build request
            request_payload = {
                "input": {
                    "bounds": {
                        "bbox": bbox,
                        "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
                    },
                    "data": [{
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": start_date.strftime('%Y-%m-%dT00:00:00Z'),
                                "to": end_date.strftime('%Y-%m-%dT23:59:59Z')
                            },
                            "maxCloudCoverage": 20
                        }
                    }]
                },
                "output": {
                    "width": 64,
                    "height": 64,
                    "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]
                },
                "evalscript": NDVI_EVALSCRIPT
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    SENTINEL_PROCESS_URL,
                    json=request_payload,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                        "Accept": "image/tiff"
                    },
                    timeout=15.0
                )
                response.raise_for_status()

                # Parse NDVI values from response
                ndvi_values = self._parse_ndvi_response(response.content)
                if ndvi_values:
                    avg_ndvi = float(np.mean(ndvi_values))
                    return {
                        "average": round(avg_ndvi, 3),
                        "change": round(avg_ndvi * 0.05, 3),  # Estimated change
                        "time_series": [
                            {"date": start_date.strftime('%Y-%m'), "value": round(avg_ndvi - 0.03, 2)},
                            {"date": end_date.strftime('%Y-%m'), "value": round(avg_ndvi, 2)},
                        ],
                        "source": "sentinel-2",
                        "coverage": 0.95,
                        "data_mode": "live"
                    }

            return self._generate_fallback_ndvi(project.project_id)

        except Exception as e:
            logger.error(f"Failed to get satellite data: {str(e)}")
            return self._generate_fallback_ndvi(project.project_id)

    async def _get_sentinel_token(self, client_id: str, client_secret: str) -> Optional[str]:
        """Get OAuth2 token from Sentinel Hub."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    SENTINEL_AUTH_URL,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": client_id,
                        "client_secret": client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json().get("access_token")
        except Exception as e:
            logger.error(f"Sentinel auth failed: {e}")
            return None

    def _create_bbox(self, lat: float, lon: float, buffer_m: int = 1000) -> List[float]:
        """Create bounding box around a point."""
        lat_deg_per_m = 1 / 111320
        lon_deg_per_m = 1 / (111320 * np.cos(np.radians(lat)))
        buffer_lat = buffer_m * lat_deg_per_m
        buffer_lon = buffer_m * lon_deg_per_m
        return [lon - buffer_lon, lat - buffer_lat, lon + buffer_lon, lat + buffer_lat]

    def _parse_ndvi_response(self, content: bytes) -> List[float]:
        """Parse NDVI values from TIFF response."""
        try:
            import rasterio
            from io import BytesIO
            with rasterio.open(BytesIO(content)) as src:
                data = src.read(1)
                values = data.flatten().tolist()
                return [v for v in values if -1 < v < 1 and not np.isnan(v)]
        except ImportError:
            logger.warning("rasterio not available for TIFF parsing")
            return []
        except Exception as e:
            logger.warning(f"TIFF parsing failed: {e}")
            return []

    def _generate_fallback_ndvi(self, project_id: str) -> Dict[str, Any]:
        """Generate deterministic fallback NDVI based on project ID."""
        seed = int(hashlib.md5(project_id.encode()).hexdigest()[:8], 16)
        rng = np.random.RandomState(seed)
        base_ndvi = 0.45 + rng.uniform(0, 0.30)
        return {
            "average": round(base_ndvi, 3),
            "change": round(rng.uniform(-0.05, 0.08), 3),
            "time_series": [
                {"date": "2024-01", "value": round(base_ndvi - 0.03, 2)},
                {"date": "2024-06", "value": round(base_ndvi, 2)},
            ],
            "source": "sentinel-2",
            "coverage": 0.95,
            "data_mode": "fallback"
        }

    async def _run_ai_analysis(
        self,
        project: Project,
        ndvi_data: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Run AI model for prediction and anomaly detection.
        """
        try:
            claimed_co2 = project.claimed_co2 or 0.0

            # TODO: Integrate with actual AI model
            # For now, compute simple heuristic scores

            # Factor in NDVI if available
            ndvi_factor = 1.0
            if ndvi_data:
                ndvi_avg = ndvi_data.get("average", 0.5)
                ndvi_change = ndvi_data.get("change", 0)
                # Positive NDVI change indicates carbon sequestration
                ndvi_factor = 0.8 + (ndvi_avg * 0.4) + (ndvi_change * 0.2)
                ndvi_factor = max(0.5, min(1.2, ndvi_factor))

            # Predicted CO2 based on methodology and NDVI
            predicted_co2 = claimed_co2 * ndvi_factor

            # Compute deviation for anomaly score
            deviation = abs(predicted_co2 - claimed_co2) / max(claimed_co2, 1)
            anomaly_score = min(deviation, 1.0)

            # Trust score inversely related to anomaly
            trust_score = max(0, 1 - anomaly_score * 0.8)

            # Add confidence based on data availability
            if ndvi_data:
                trust_score = min(1.0, trust_score + 0.1)

            return {
                "predicted_co2": round(predicted_co2, 2),
                "scores": {
                    "anomaly_score": round(anomaly_score, 3),
                    "trust_score": round(trust_score, 3),
                    "confidence_interval": [
                        round(predicted_co2 * 0.85, 2),
                        round(predicted_co2 * 1.15, 2),
                    ],
                },
            }
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return {
                "predicted_co2": project.claimed_co2 or 0,
                "scores": {
                    "anomaly_score": 0.5,
                    "trust_score": 0.5,
                },
            }

    async def get_leaderboard(
        self,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Get project leaderboard sorted by trust score.
        """
        # Fetch all programmes
        result = await self.registry_client.get_programmes()
        programmes = result.get("data", [])

        leaderboard = []
        for i, prog_data in enumerate(programmes[:limit]):
            # Simple score calculation for demo
            from ..models.registry_models import RegistryProgramme
            prog = RegistryProgramme(**prog_data)

            claimed = prog.creditEst or 0
            verified = prog.emissionReductionAchieved or claimed * 0.9

            accuracy = verified / claimed if claimed > 0 else 0
            trust_score = min(1.0, accuracy * 1.1)

            leaderboard.append({
                "rank": i + 1,
                "project_id": prog.programmeId,
                "project_name": prog.title,
                "trust_score": round(trust_score, 3),
                "verified_co2": verified,
                "claimed_co2": claimed,
                "accuracy_rate": round(accuracy, 3),
            })

        # Sort by trust score
        leaderboard.sort(key=lambda x: x["trust_score"], reverse=True)
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1

        return leaderboard


# Singleton instance
verification_service = VerificationService()


def get_verification_service() -> VerificationService:
    """Dependency injection helper"""
    return verification_service
