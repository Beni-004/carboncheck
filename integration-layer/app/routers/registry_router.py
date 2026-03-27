"""
Registry API Router
Exposes endpoints for registry integration.
Acts as bridge between FastAPI and UNDP Registry Service.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import logging

from ..models.registry_models import (
    Project,
    VerificationRequest,
    VerificationResult,
    RegistryProjectQuery,
    ProjectCreateRequest,
    RegistryStatistics,
    LeaderboardEntry,
)
from ..services.registry_client import (
    RegistryServiceClient,
    RegistryServiceError,
    get_registry_client,
)
from ..services.verification_service import (
    VerificationService,
    get_verification_service,
)
from ..mappers.programme_mapper import ProgrammeMapper

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registry", tags=["Registry Integration"])


# ============== Project Endpoints ==============

@router.get(
    "/projects",
    response_model=dict,
    summary="Get registry projects",
    description="Fetch projects from UNDP registry with optional filters",
)
async def get_projects(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    stage: Optional[str] = None,
    sector: Optional[str] = None,
    country_code: Optional[str] = None,
    company_id: Optional[int] = None,
    registry_client: RegistryServiceClient = Depends(get_registry_client),
):
    """
    Get list of projects from the UNDP registry.
    Maps Programme entities to Project format.
    """
    try:
        query = RegistryProjectQuery(
            page=page,
            size=size,
            stage=stage,
            sector=sector,
            country_code=country_code,
            company_id=company_id,
        )
        result = await registry_client.get_programmes(query)

        # Map programmes to projects
        projects = []
        for prog_data in result.get("data", []):
            from ..models.registry_models import RegistryProgramme
            prog = RegistryProgramme(**prog_data)
            project = ProgrammeMapper.to_project(prog)
            projects.append(project.model_dump())

        return {
            "data": projects,
            "total": result.get("total", len(projects)),
            "page": page,
            "size": size,
        }
    except RegistryServiceError as e:
        logger.error(f"Registry error: {str(e)}")
        raise HTTPException(status_code=e.status_code or 502, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/projects/{project_id}",
    response_model=Project,
    summary="Get project by ID",
)
async def get_project(
    project_id: str,
    registry_client: RegistryServiceClient = Depends(get_registry_client),
):
    """Get a specific project from the registry by ID"""
    try:
        programme = await registry_client.get_programme(project_id)
        return ProgrammeMapper.to_project(programme)
    except RegistryServiceError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        raise HTTPException(status_code=e.status_code or 502, detail=str(e))


@router.post(
    "/projects",
    response_model=Project,
    summary="Create new project",
    description="Create a new project in the UNDP registry",
)
async def create_project(
    request: ProjectCreateRequest,
    registry_client: RegistryServiceClient = Depends(get_registry_client),
):
    """Create a new project in the registry"""
    try:
        programme_data = ProgrammeMapper.to_programme_create(request)
        programme = await registry_client.create_programme(programme_data)
        return ProgrammeMapper.to_project(programme)
    except RegistryServiceError as e:
        raise HTTPException(status_code=e.status_code or 502, detail=str(e))


@router.post(
    "/projects/{project_id}/verify",
    response_model=VerificationResult,
    summary="Verify project",
    description="Run verification pipeline on a project",
)
async def verify_project(
    project_id: str,
    include_satellite: bool = Query(True, description="Include satellite NDVI analysis"),
    include_ai: bool = Query(True, description="Include AI prediction"),
    verification_service: VerificationService = Depends(get_verification_service),
):
    """
    Run full verification pipeline on a project:
    1. Fetch registry data (Ground Layer)
    2. Get satellite NDVI data (Satellite Layer)
    3. Run AI prediction (AI Layer)
    4. Compute trust score (Scoring Layer)
    """
    try:
        request = VerificationRequest(
            project_id=project_id,
            include_satellite=include_satellite,
            include_ai_analysis=include_ai,
        )
        result = await verification_service.verify_project(request)
        return result
    except RegistryServiceError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
        raise HTTPException(status_code=e.status_code or 502, detail=str(e))
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


# ============== Credit Operation Endpoints ==============

@router.post(
    "/projects/{project_id}/authorize",
    response_model=Project,
    summary="Authorize project",
)
async def authorize_project(
    project_id: str,
    registry_client: RegistryServiceClient = Depends(get_registry_client),
):
    """Authorize a project in the registry"""
    try:
        programme = await registry_client.authorize_programme(project_id)
        return ProgrammeMapper.to_project(programme)
    except RegistryServiceError as e:
        raise HTTPException(status_code=e.status_code or 502, detail=str(e))


@router.post(
    "/projects/{project_id}/issue-credits",
    response_model=Project,
    summary="Issue credits",
)
async def issue_credits(
    project_id: str,
    credit_amount: float = Query(..., gt=0),
    comment: Optional[str] = None,
    registry_client: RegistryServiceClient = Depends(get_registry_client),
):
    """Issue credits to a project"""
    try:
        programme = await registry_client.issue_credits(
            programme_id=project_id,
            credit_amount=credit_amount,
            comment=comment,
        )
        return ProgrammeMapper.to_project(programme)
    except RegistryServiceError as e:
        raise HTTPException(status_code=e.status_code or 502, detail=str(e))


@router.post(
    "/projects/{project_id}/transfer-credits",
    response_model=Project,
    summary="Transfer credits",
)
async def transfer_credits(
    project_id: str,
    from_company_id: int = Query(...),
    to_company_id: int = Query(...),
    credit_amount: float = Query(..., gt=0),
    comment: Optional[str] = None,
    registry_client: RegistryServiceClient = Depends(get_registry_client),
):
    """Transfer credits between companies"""
    try:
        programme = await registry_client.transfer_credits(
            programme_id=project_id,
            from_company_id=from_company_id,
            to_company_id=to_company_id,
            credit_amount=credit_amount,
            comment=comment,
        )
        return ProgrammeMapper.to_project(programme)
    except RegistryServiceError as e:
        raise HTTPException(status_code=e.status_code or 502, detail=str(e))


@router.post(
    "/projects/{project_id}/retire-credits",
    response_model=Project,
    summary="Retire credits",
)
async def retire_credits(
    project_id: str,
    company_id: int = Query(...),
    credit_amount: float = Query(..., gt=0),
    retirement_type: Optional[str] = None,
    comment: Optional[str] = None,
    registry_client: RegistryServiceClient = Depends(get_registry_client),
):
    """Retire credits from a project"""
    try:
        programme = await registry_client.retire_credits(
            programme_id=project_id,
            company_id=company_id,
            credit_amount=credit_amount,
            retirement_type=retirement_type,
            comment=comment,
        )
        return ProgrammeMapper.to_project(programme)
    except RegistryServiceError as e:
        raise HTTPException(status_code=e.status_code or 502, detail=str(e))


# ============== Statistics & Leaderboard ==============

@router.get(
    "/statistics",
    response_model=RegistryStatistics,
    summary="Get registry statistics",
)
async def get_statistics(
    registry_client: RegistryServiceClient = Depends(get_registry_client),
):
    """Get aggregated statistics from the registry"""
    try:
        return await registry_client.get_statistics()
    except RegistryServiceError as e:
        raise HTTPException(status_code=e.status_code or 502, detail=str(e))


@router.get(
    "/leaderboard",
    response_model=List[dict],
    summary="Get project leaderboard",
)
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    verification_service: VerificationService = Depends(get_verification_service),
):
    """Get project leaderboard sorted by trust score"""
    try:
        return await verification_service.get_leaderboard(limit=limit)
    except Exception as e:
        logger.error(f"Leaderboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Health Check ==============

@router.get(
    "/health",
    summary="Check registry service health",
)
async def health_check(
    registry_client: RegistryServiceClient = Depends(get_registry_client),
):
    """Check if registry service is reachable"""
    is_healthy = await registry_client.health_check()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "registry_service": "connected" if is_healthy else "disconnected",
    }
