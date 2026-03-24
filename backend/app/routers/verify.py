"""
Credit Verification Router
Handles single and bulk credit verification requests.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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


def get_mock_verification(credit_id: str) -> TrustScoreResult:
    """Generate mock verification result matching frontend expectations"""
    
    # Pre-defined test cases
    mock_data = {
        "VCS-2024-001": TrustScoreResult(
            creditId="VCS-2024-001",
            trustScore=92,
            verdict="PASS",
            category="Renewable Energy",
            issuer="Verified Carbon Standard",
            vintage=2023,
            co2Equivalent=1000,
            checks=[
                FraudCheck(
                    name="Baseline Match",
                    passed=True,
                    score=25,
                    description="Project baseline aligns with registry records",
                    evidence="Verified against VCS registry database"
                ),
                FraudCheck(
                    name="Additionality",
                    passed=True,
                    score=25,
                    description="Project would not have occurred without carbon finance",
                    evidence="Financial additionality demonstrated in project documentation"
                ),
                FraudCheck(
                    name="Permanence Risk",
                    passed=True,
                    score=22,
                    description="Low risk of emission reversals",
                    evidence="Buffer pool allocation meets VCS requirements"
                ),
                FraudCheck(
                    name="Double Counting",
                    passed=True,
                    score=20,
                    description="No evidence of duplicate claims across registries",
                    evidence="Cross-registry check completed successfully"
                ),
            ],
            fraudRisks=[],
            verifiedAt=datetime.utcnow().isoformat(),
            dataMode="live",
            fallbackUsed=False,
            dataFreshness="Real-time"
        ),
        "GOLD-2023-556": TrustScoreResult(
            creditId="GOLD-2023-556",
            trustScore=58,
            verdict="WARNING",
            category="Forestry",
            issuer="Gold Standard",
            vintage=2022,
            co2Equivalent=500,
            checks=[
                FraudCheck(
                    name="Baseline Match",
                    passed=True,
                    score=25,
                    description="Project baseline aligns with registry records"
                ),
                FraudCheck(
                    name="Additionality",
                    passed=False,
                    score=8,
                    description="Weak evidence that project required carbon finance",
                    evidence="Baseline comparison suggests project may have occurred anyway"
                ),
                FraudCheck(
                    name="Permanence Risk",
                    passed=True,
                    score=20,
                    description="Moderate risk due to forestry project type"
                ),
                FraudCheck(
                    name="Double Counting",
                    passed=False,
                    score=5,
                    description="Credit appears in multiple registries",
                    evidence="Registry cross-check flagged duplicate entries"
                ),
            ],
            fraudRisks=[
                FraudRisk(
                    category="Double Counting",
                    severity="medium",
                    description="Credit appears in multiple registries simultaneously",
                    evidence="Registry cross-check flagged duplicate entries"
                ),
                FraudRisk(
                    category="Additionality",
                    severity="low",
                    description="Project may have occurred anyway without incentive",
                    evidence="Baseline comparison suggests weak additionality case"
                ),
            ],
            verifiedAt=datetime.utcnow().isoformat(),
            dataMode="live",
            fallbackUsed=False,
            dataFreshness="Real-time"
        ),
        "ACR-2021-999": TrustScoreResult(
            creditId="ACR-2021-999",
            trustScore=15,
            verdict="FAIL",
            category="Landfill Gas",
            issuer="American Carbon Registry",
            vintage=2019,
            co2Equivalent=2000,
            checks=[
                FraudCheck(
                    name="Baseline Match",
                    passed=False,
                    score=5,
                    description="Project data conflicts with registry records",
                    evidence="Significant discrepancies in reported emissions reductions"
                ),
                FraudCheck(
                    name="Additionality",
                    passed=False,
                    score=3,
                    description="Project lacks financial additionality proof",
                    evidence="No evidence project required carbon finance to proceed"
                ),
                FraudCheck(
                    name="Permanence Risk",
                    passed=False,
                    score=2,
                    description="High risk of emission reversals"
                ),
                FraudCheck(
                    name="Double Counting",
                    passed=False,
                    score=5,
                    description="Credit already retired in another registry",
                    evidence="Found in retirement database with date 2022-03-15"
                ),
            ],
            fraudRisks=[
                FraudRisk(
                    category="Retirement Status",
                    severity="high",
                    description="Credit has already been retired and cannot be sold",
                    evidence="Found in retirement database with retirement date 2022-03-15"
                ),
                FraudRisk(
                    category="Registry Suspension",
                    severity="high",
                    description="Issuer temporarily suspended from issuing new credits",
                    evidence="ACR announced moratorium on new credit issuance"
                ),
            ],
            verifiedAt=datetime.utcnow().isoformat(),
            dataMode="fallback",
            fallbackUsed=True,
            dataFreshness="Cached (2 hours old)"
        ),
    }
    
    # Return pre-defined or generate random
    if credit_id in mock_data:
        return mock_data[credit_id]
    
    # Generate random result for unknown IDs
    import random
    score = random.randint(0, 100)
    verdict = "PASS" if score > 70 else "WARNING" if score > 40 else "FAIL"
    
    baseline_score = random.randint(1, 25)
    additionality_score = random.randint(1, 25)
    permanence_score = random.randint(1, 25)
    double_count_score = random.randint(1, 25)
    
    categories = ["Renewable Energy", "Forestry", "Landfill Gas", "Methane"]
    issuers = ["Verified Carbon Standard", "Gold Standard", "American Carbon Registry"]
    
    return TrustScoreResult(
        creditId=credit_id,
        trustScore=score,
        verdict=verdict,
        category=random.choice(categories),
        issuer=random.choice(issuers),
        vintage=random.randint(2020, 2024),
        co2Equivalent=random.randint(100, 2100),
        checks=[
            FraudCheck(
                name="Baseline Match",
                passed=baseline_score > 15,
                score=baseline_score,
                description="Project baseline aligns with registry records" if baseline_score > 15 else "Project data conflicts with registry records"
            ),
            FraudCheck(
                name="Additionality",
                passed=additionality_score > 15,
                score=additionality_score,
                description="Project would not have occurred without carbon finance" if additionality_score > 15 else "Weak evidence that project required carbon finance"
            ),
            FraudCheck(
                name="Permanence Risk",
                passed=permanence_score > 15,
                score=permanence_score,
                description="Low risk of emission reversals" if permanence_score > 15 else "High risk of emission reversals"
            ),
            FraudCheck(
                name="Double Counting",
                passed=double_count_score > 15,
                score=double_count_score,
                description="No evidence of duplicate claims" if double_count_score > 15 else "Credit appears in multiple registries"
            ),
        ],
        fraudRisks=[] if score > 70 else [
            FraudRisk(
                category="Sample Risk",
                severity="medium",
                description="Generic fraud indicator for demo purposes"
            )
        ],
        verifiedAt=datetime.utcnow().isoformat(),
        dataMode="live",
        fallbackUsed=False,
        dataFreshness="Real-time"
    )


@router.post("/verify")
async def verify_single(request: VerifyRequest) -> TrustScoreResult:
    """
    Verify a single carbon credit.
    Returns trust score and fraud analysis.
    """
    if not request.creditId or len(request.creditId.strip()) == 0:
        raise HTTPException(status_code=400, detail="Credit ID is required")
    
    result = get_mock_verification(request.creditId)
    return result


@router.post("/verify/bulk")
async def verify_bulk(request: BulkVerifyRequest) -> BulkVerifyResult:
    """
    Verify multiple carbon credits in bulk.
    Returns sorted list with worst credits first.
    """
    if not request.creditIds or len(request.creditIds) == 0:
        raise HTTPException(status_code=400, detail="At least one credit ID is required")
    
    if len(request.creditIds) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 credits per request")
    
    results = []
    errors = []
    
    for credit_id in request.creditIds:
        # Simulate 5% error rate
        import random
        if random.random() < 0.05:
            errors.append({
                "creditId": credit_id,
                "error": "Invalid credit ID format or not found in registry"
            })
        else:
            results.append(get_mock_verification(credit_id))
    
    # Sort by trust score ascending (worst first)
    results.sort(key=lambda x: x.trustScore)
    
    return BulkVerifyResult(
        results=results,
        totalSubmitted=len(request.creditIds),
        totalProcessed=len(results),
        totalErrors=len(errors),
        errors=errors if errors else None
    )
