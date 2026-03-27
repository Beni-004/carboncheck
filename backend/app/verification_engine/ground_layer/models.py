"""
Data models for registry information.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProjectLocation(BaseModel):
    """Geospatial location of a carbon project."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    country: Optional[str] = None
    region: Optional[str] = None


class RegistryProject(BaseModel):
    """
    Normalized representation of a carbon credit project
    across different registries (Verra, Gold Standard, ACR).
    """
    project_id: str
    registry: str  # "verra", "gold_standard", "acr"
    project_name: Optional[str] = None
    location: ProjectLocation
    
    # Carbon metrics
    claimed_co2_tons: float
    vintage_year: int
    
    # Project details
    methodology: str
    project_type: str  # "forestry", "renewable", "soil", etc.
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Documentation
    registry_url: Optional[str] = None
    pdf_documents: List[str] = Field(default_factory=list)
    
    # Metadata
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class PDFExtraction(BaseModel):
    """Extracted data from project design documents."""
    claimed_carbon: Optional[float] = None
    baseline_carbon: Optional[float] = None
    project_area_ha: Optional[float] = None
    methodology_description: Optional[str] = None
    tables: List[dict] = Field(default_factory=list)
