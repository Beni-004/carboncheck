"""
Data Mapper: UNDP Registry <-> CarbonCheck
Handles bidirectional mapping between data structures.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from ..models.registry_models import (
    RegistryProgramme,
    RegistryProgrammeStage,
    RegistrySector,
    Project,
    VerificationResult,
    ProjectCreateRequest,
)


class ProgrammeMapper:
    """
    Maps UNDP Programme entities to CarbonCheck Project entities.

    Field Mappings:
    - Programme.programmeId -> Project.project_id
    - Programme.title -> Project.name
    - Programme.creditEst -> Project.claimed_co2
    - Programme.sector -> Project.methodology
    - Programme.geographicalLocationCordintes -> Project.region
    - Programme.currentStage -> Project.status
    """

    # Stage mapping from UNDP to CarbonCheck
    STAGE_MAP = {
        RegistryProgrammeStage.AWAITING_AUTHORIZATION: "pending",
        RegistryProgrammeStage.PENDING: "pending",
        RegistryProgrammeStage.AUTHORIZED: "authorized",
        RegistryProgrammeStage.REJECTED: "rejected",
        RegistryProgrammeStage.CREDIT_ISSUED: "active",
        RegistryProgrammeStage.CREDIT_TRANSFERRED: "active",
        RegistryProgrammeStage.CREDIT_RETIRED: "completed",
    }

    # Sector to methodology mapping
    SECTOR_TO_METHODOLOGY = {
        RegistrySector.Energy: "renewable_energy",
        RegistrySector.Forestry: "afforestation_reforestation",
        RegistrySector.Agriculture: "agricultural_land_management",
        RegistrySector.Waste: "waste_management",
        RegistrySector.Transport: "transport_efficiency",
        RegistrySector.Manufacturing: "industrial_efficiency",
        RegistrySector.Other: "other",
    }

    @classmethod
    def to_project(cls, programme: RegistryProgramme) -> Project:
        """Convert UNDP Programme to CarbonCheck Project"""

        # Extract region from geographical coordinates
        region = None
        if programme.geographicalLocationCordintes:
            region = cls._extract_region(programme.geographicalLocationCordintes)

        # Map sector to methodology
        methodology = None
        if programme.sector:
            methodology = cls.SECTOR_TO_METHODOLOGY.get(programme.sector, "other")

        # Map stage to status
        status = cls.STAGE_MAP.get(programme.currentStage, "pending")

        # Convert timestamps to datetime
        start_date = None
        end_date = None
        if programme.startTime:
            start_date = datetime.fromtimestamp(programme.startTime / 1000)
        if programme.endTime:
            end_date = datetime.fromtimestamp(programme.endTime / 1000)

        return Project(
            project_id=programme.programmeId,
            name=programme.title,
            external_id=programme.externalId,
            methodology=methodology,
            region=region,
            country_code=programme.countryCodeA2,
            status=status,
            claimed_co2=programme.creditEst,
            verified_co2=programme.emissionReductionAchieved,
            credits_issued=programme.creditIssued,
            credits_balance=programme.creditBalance,
            start_date=start_date,
            end_date=end_date,
            location_coordinates=programme.geographicalLocationCordintes,
            metadata={
                "sectoral_scope": programme.sectoralScope,
                "sector": programme.sector.value if programme.sector else None,
                "credit_unit": programme.creditUnit,
                "company_ids": programme.companyId,
                "programme_properties": programme.programmeProperties,
                "credit_retired": programme.creditRetired,
                "credit_transferred": programme.creditTransferred,
            },
            created_at=programme.createdAt,
            updated_at=programme.updatedAt,
        )

    @classmethod
    def to_programme_create(cls, project: ProjectCreateRequest) -> Dict[str, Any]:
        """Convert CarbonCheck ProjectCreateRequest to UNDP Programme create DTO"""

        # Reverse methodology mapping
        sector = None
        if project.methodology:
            for k, v in cls.SECTOR_TO_METHODOLOGY.items():
                if v == project.methodology:
                    sector = k.value
                    break

        # Convert dates to timestamps
        start_time = None
        end_time = None
        if project.start_date:
            start_time = int(project.start_date.timestamp() * 1000)
        if project.end_date:
            end_time = int(project.end_date.timestamp() * 1000)

        return {
            "title": project.name,
            "externalId": project.external_id,
            "sector": sector,
            "countryCodeA2": project.country_code,
            "creditEst": project.claimed_co2,
            "startTime": start_time,
            "endTime": end_time,
            "geographicalLocationCordintes": project.location_coordinates,
            "companyId": project.company_ids,
            "programmeProperties": project.metadata,
        }

    @classmethod
    def _extract_region(cls, coordinates: Dict[str, Any]) -> Optional[str]:
        """Extract region name from geographical coordinates"""
        if isinstance(coordinates, dict):
            # Try common field names
            for field in ["region", "province", "state", "area", "name"]:
                if field in coordinates:
                    return coordinates[field]
            # If coordinates are nested
            if "properties" in coordinates:
                return cls._extract_region(coordinates["properties"])
        return None


class VerificationMapper:
    """
    Maps verification results between systems.
    """

    # Verdict mapping based on trust score thresholds
    SCORE_THRESHOLDS = {
        "VERIFIED": 0.7,
        "FLAGGED": 0.4,
        "REJECTED": 0.0,
    }

    @classmethod
    def compute_verdict(cls, trust_score: float, anomaly_score: float) -> str:
        """Compute verification verdict from scores"""
        if anomaly_score > 0.8:
            return "REJECTED"
        if trust_score >= cls.SCORE_THRESHOLDS["VERIFIED"]:
            return "VERIFIED"
        if trust_score >= cls.SCORE_THRESHOLDS["FLAGGED"]:
            return "FLAGGED"
        return "REJECTED"

    @classmethod
    def create_result(
        cls,
        project_id: str,
        predicted_co2: float,
        claimed_co2: float,
        ndvi_data: Optional[Dict[str, Any]] = None,
        ai_scores: Optional[Dict[str, Any]] = None,
    ) -> VerificationResult:
        """Create a verification result from pipeline outputs"""

        ndvi_avg = None
        ndvi_change = None
        if ndvi_data:
            ndvi_avg = ndvi_data.get("average")
            ndvi_change = ndvi_data.get("change")

        anomaly_score = 0.0
        trust_score = 0.5
        confidence_interval = None

        if ai_scores:
            anomaly_score = ai_scores.get("anomaly_score", 0.0)
            trust_score = ai_scores.get("trust_score", 0.5)
            confidence_interval = ai_scores.get("confidence_interval")

        verdict = cls.compute_verdict(trust_score, anomaly_score)

        data_sources = ["registry"]
        if ndvi_data:
            data_sources.append("satellite_ndvi")
        if ai_scores:
            data_sources.append("ai_model")

        return VerificationResult(
            project_id=project_id,
            predicted_co2=predicted_co2,
            claimed_co2=claimed_co2,
            ndvi_avg=ndvi_avg,
            ndvi_change=ndvi_change,
            anomaly_score=anomaly_score,
            trust_score=trust_score,
            confidence_interval=confidence_interval,
            verdict=verdict,
            verification_timestamp=datetime.utcnow(),
            data_sources=data_sources,
            metadata={
                "raw_ndvi_data": ndvi_data,
                "raw_ai_scores": ai_scores,
            },
        )
