"""
Credit Verification Router
Handles single and bulk credit verification requests.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.verify_service import verify_single, verify_bulk

router = APIRouter()


class VerifyRequest(BaseModel):
    creditId: str


class BulkVerifyRequest(BaseModel):
    creditIds: List[str]


class FraudCheck(BaseModel):
    name: str
    passed: bool
    score: int
    description: str
    evidence: Optional[str] = None


class FraudRisk(BaseModel):
    category: str
    severity: str
    description: str
    evidence: Optional[str] = None


class TrustScoreResult(BaseModel):
    creditId: str
    trustScore: int
    verdict: str
    category: str
    issuer: str
    vintage: int
    co2Equivalent: int
    checks: List[FraudCheck]
    fraudRisks: List[FraudRisk]
    verifiedAt: str
    dataMode: Optional[str] = "live"
    fallbackUsed: Optional[bool] = False
    dataFreshness: Optional[str] = "Real-time"


class BulkVerifyResult(BaseModel):
    results: List[TrustScoreResult]
    totalSubmitted: int
    totalProcessed: int
    totalErrors: int
    errors: Optional[List[dict]] = None


@router.post("/verify")
async def verify_single_endpoint(request: VerifyRequest) -> TrustScoreResult:
    """
    Verify a single carbon credit.
    Returns trust score and fraud analysis.
    """
    if not request.creditId or len(request.creditId.strip()) == 0:
        raise HTTPException(status_code=400, detail="Credit ID is required")
    
    result = await verify_single(request.creditId)
    return TrustScoreResult(**result)


@router.post("/verify/bulk")
async def verify_bulk_endpoint(request: BulkVerifyRequest) -> BulkVerifyResult:
    """
    Verify multiple carbon credits in bulk.
    Returns sorted list with worst credits first.
    """
    if not request.creditIds or len(request.creditIds) == 0:
        raise HTTPException(status_code=400, detail="At least one credit ID is required")
    
    if len(request.creditIds) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 credits per request")
    
    result = await verify_bulk(request.creditIds)
    return BulkVerifyResult(**result)
