"""
Credit Verification Router
Handles single and bulk credit verification requests.
Configured for multi-layer verification engine with extended timeouts.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from app.services.verify_service import verify_single, verify_bulk
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Timeout configuration for multi-layer verification engine
SINGLE_VERIFY_TIMEOUT = 25  # seconds (accounts for 10-20s cold start + buffer)
BULK_VERIFY_TIMEOUT = 60  # seconds for bulk operations


class VerifyRequest(BaseModel):
    creditId: str = Field(..., min_length=1, max_length=100)

    @validator('creditId')
    def validate_credit_id(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Credit ID cannot be empty')
        # Basic format validation (can be extended)
        if len(v) < 3:
            raise ValueError('Credit ID must be at least 3 characters')
        return v


class BulkVerifyRequest(BaseModel):
    creditIds: List[str] = Field(..., min_items=1, max_items=50)

    @validator('creditIds')
    def validate_credit_ids(cls, v):
        if not v:
            raise ValueError('At least one credit ID is required')
        if len(v) > 50:
            raise ValueError('Maximum 50 credits per request')
        # Strip and validate each ID
        cleaned = [id.strip() for id in v if id.strip()]
        if not cleaned:
            raise ValueError('No valid credit IDs provided')
        return cleaned


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
    projectUrl: Optional[str] = None


class BulkVerifyResult(BaseModel):
    results: List[TrustScoreResult]
    totalSubmitted: int
    totalProcessed: int
    totalErrors: int
    errors: Optional[List[dict]] = None


@router.post("/verify", response_model=TrustScoreResult)
async def verify_single_endpoint(request: VerifyRequest) -> TrustScoreResult:
    """
    Verify a single carbon credit using multi-layer verification engine.
    
    This endpoint performs deep analysis including:
    - Ground layer: Registry data validation
    - Satellite layer: Remote sensing verification
    - AI layer: Fraud pattern detection
    - Scoring layer: Trust score computation
    
    Expected response time: 10-20 seconds for cold starts, <5s for warm cache.
    
    Returns:
        TrustScoreResult: Comprehensive trust score and fraud analysis
        
    Raises:
        HTTPException: 400 for invalid input, 408 for timeout, 500 for engine errors
    """
    logger.info(f"Single verification request for credit ID: {request.creditId}")
    
    try:
        # Apply timeout to prevent hung requests
        result = await asyncio.wait_for(
            verify_single(request.creditId),
            timeout=SINGLE_VERIFY_TIMEOUT
        )
        
        logger.info(
            f"Verification completed for {request.creditId}: "
            f"score={result.get('trustScore')}, verdict={result.get('verdict')}"
        )
        
        return TrustScoreResult(**result)
        
    except asyncio.TimeoutError:
        logger.error(f"Verification timeout for credit ID: {request.creditId}")
        raise HTTPException(
            status_code=408,
            detail=f"Verification timeout after {SINGLE_VERIFY_TIMEOUT}s. "
                   "The multi-layer engine is under heavy load. Please retry."
        )
    except ValueError as e:
        logger.warning(f"Invalid credit ID {request.creditId}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Verification engine error for {request.creditId}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Verification engine encountered an error. Please try again."
        )


@router.post("/verify/bulk", response_model=BulkVerifyResult)
async def verify_bulk_endpoint(request: BulkVerifyRequest) -> BulkVerifyResult:
    """
    Verify multiple carbon credits in bulk using parallel execution.
    
    Processes up to 50 credits concurrently with individual timeout handling.
    Results are sorted by risk (highest risk first) for audit triage.
    
    Expected response time: Variable based on batch size and cache state.
    
    Returns:
        BulkVerifyResult: Ranked results with per-ID error handling
        
    Raises:
        HTTPException: 400 for invalid input, 408 for timeout, 500 for engine errors
    """
    credit_count = len(request.creditIds)
    logger.info(f"Bulk verification request for {credit_count} credits")
    
    try:
        # Apply timeout scaled to batch size
        timeout = min(BULK_VERIFY_TIMEOUT, credit_count * 2)
        
        result = await asyncio.wait_for(
            verify_bulk(request.creditIds),
            timeout=timeout
        )
        
        logger.info(
            f"Bulk verification completed: "
            f"submitted={result.get('totalSubmitted')}, "
            f"processed={result.get('totalProcessed')}, "
            f"errors={result.get('totalErrors')}"
        )
        
        return BulkVerifyResult(**result)
        
    except asyncio.TimeoutError:
        logger.error(f"Bulk verification timeout for {credit_count} credits")
        raise HTTPException(
            status_code=408,
            detail=f"Bulk verification timeout after {timeout}s. "
                   "Try reducing batch size or retry later."
        )
    except ValueError as e:
        logger.warning(f"Invalid bulk request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Bulk verification engine error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Bulk verification engine encountered an error. Please try again."
        )
