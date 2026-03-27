"""
Pydantic models for the integration layer.
Maps between UNDP Registry structures and CarbonCheck system.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============== UNDP Registry Models (Input) ==============

class RegistryProgrammeStage(str, Enum):
    """UNDP Registry programme lifecycle stages"""
    AWAITING_AUTHORIZATION = "AwaitingAuthorization"
    PENDING = "Pending"
    AUTHORIZED = "Authorised"
    REJECTED = "Rejected"
    CREDIT_ISSUED = "CreditIssued"
    CREDIT_TRANSFERRED = "CreditTransferred"
    CREDIT_RETIRED = "CreditRetired"


class RegistrySector(str, Enum):
    """UNDP Registry programme sectors"""
    Energy = "Energy"
    Health = "Health"
    Education = "Education"
    Transport = "Transport"
    Manufacturing = "Manufacturing"
    Hospitality = "Hospitality"
    Forestry = "Forestry"
    Waste = "Waste"
    Agriculture = "Agriculture"
    Other = "Other"


class RegistryProgramme(BaseModel):
    """UNDP Registry Programme structure"""
    programmeId: str
    serialNo: Optional[str] = None
    title: str
    externalId: Optional[str] = None
    sectoralScope: Optional[str] = None
    sector: Optional[RegistrySector] = None
    countryCodeA2: Optional[str] = None
    currentStage: RegistryProgrammeStage = RegistryProgrammeStage.AWAITING_AUTHORIZATION
    startTime: Optional[int] = None
    endTime: Optional[int] = None
    creditEst: Optional[float] = None
    emissionReductionExpected: Optional[float] = None
    emissionReductionAchieved: Optional[float] = None
    creditIssued: Optional[float] = None
    creditBalance: Optional[float] = None
    creditRetired: Optional[List[float]] = None
    creditTransferred: Optional[List[float]] = None
    companyId: Optional[List[int]] = None
    creditUnit: Optional[str] = None
    programmeProperties: Optional[Dict[str, Any]] = None
    geographicalLocationCordintes: Optional[Dict[str, Any]] = None
    projectLocation: Optional[List[Dict[str, Any]]] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class RegistryCompany(BaseModel):
    """UNDP Registry Company structure"""
    companyId: int
    taxId: Optional[str] = None
    name: str
    email: Optional[str] = None
    country: Optional[str] = None
    companyRole: str
    state: str
    creditBalance: Optional[float] = None
    programmeCount: Optional[int] = None
    regions: Optional[List[str]] = None


# ============== CarbonCheck Models (Output) ==============

class Project(BaseModel):
    """CarbonCheck Project structure (mapped from Programme)"""
    project_id: str
    name: str
    external_id: Optional[str] = None
    methodology: Optional[str] = None  # Mapped from sector
    region: Optional[str] = None  # Mapped from geographicalLocation
    country_code: Optional[str] = None
    status: str
    claimed_co2: Optional[float] = None  # Mapped from creditEst
    verified_co2: Optional[float] = None  # Mapped from emissionReductionAchieved
    credits_issued: Optional[float] = None
    credits_balance: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location_coordinates: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class VerificationRequest(BaseModel):
    """Request to verify a project"""
    project_id: str
    include_satellite: bool = True
    include_ai_analysis: bool = True
    force_refresh: bool = False


class VerificationResult(BaseModel):
    """Result from the verification pipeline"""
    project_id: str
    predicted_co2: float
    claimed_co2: float
    ndvi_avg: Optional[float] = None
    ndvi_change: Optional[float] = None
    anomaly_score: float
    trust_score: float
    confidence_interval: Optional[List[float]] = None
    verdict: str  # "VERIFIED", "FLAGGED", "REJECTED"
    verification_timestamp: datetime
    data_sources: List[str]
    metadata: Optional[Dict[str, Any]] = None


class LeaderboardEntry(BaseModel):
    """Leaderboard entry for projects"""
    rank: int
    project_id: str
    project_name: str
    organization: Optional[str] = None
    trust_score: float
    verified_co2: float
    claimed_co2: float
    accuracy_rate: float
    last_verified: Optional[datetime] = None


class RegistryStatistics(BaseModel):
    """Statistics from the registry"""
    total_programmes: int
    total_credits_issued: float
    total_credits_retired: float
    total_credits_transferred: float
    by_stage: Dict[str, int]
    by_sector: Dict[str, int]


class ProjectCreateRequest(BaseModel):
    """Request to create a new project"""
    name: str
    external_id: Optional[str] = None
    methodology: Optional[str] = None
    region: Optional[str] = None
    country_code: Optional[str] = None
    claimed_co2: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location_coordinates: Optional[Dict[str, Any]] = None
    company_ids: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None


class RegistryProjectQuery(BaseModel):
    """Query parameters for registry projects"""
    page: int = 1
    size: int = 10
    stage: Optional[str] = None
    sector: Optional[str] = None
    country_code: Optional[str] = None
    company_id: Optional[int] = None
