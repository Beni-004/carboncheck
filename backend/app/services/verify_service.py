"""
Verification Service
Real credit verification logic with 3-layer verification engine integration.
Maintains existing API contract while using Ground → Satellite → AI → Scoring layers.
"""

import httpx
import asyncio
import logging
import re
import hashlib
import json
from typing import Optional
from datetime import datetime
from app.db import get_db_client

# Import verification engine layers
from app.verification_engine.ground_layer.registry_client import RegistryClient
from app.verification_engine.satellite_layer.gee_client import GEEClient
from app.verification_engine.satellite_layer.ndvi_processor import NDVIProcessor
from app.verification_engine.ai_layer.carbon_model import CarbonEstimator
from app.verification_engine.scoring_layer.fraud_scorer import FraudScorer

logger = logging.getLogger(__name__)


async def verify_single(credit_id: str) -> dict:
    """
    Verify a single carbon credit using the 3-layer verification engine.

    Flow:
    1. Ground Layer: Fetch registry data
    2. Satellite Layer: Fetch NDVI time series
    3. AI Layer: Predict carbon from NDVI
    4. Scoring Layer: Calculate trust score

    Returns dict with verification result matching TrustScoreResult schema.
    """
    fallback_sources = []  # Track which sources used fallback

    # Determine registry from credit ID
    registry = _infer_registry(credit_id)
    project_url = _build_project_url(credit_id, registry)

    if not project_url:
        logger.warning(f"Could not parse valid registry URL from credit_id: {credit_id}")
        return build_unverified_result(credit_id, None, "Unknown Registry", "Unknown")

    try:
        # STEP 1: Ground Layer - Fetch Registry Data
        logger.info(f"[Ground Layer] Fetching registry data for {credit_id}")
        registry_client = RegistryClient()

        ground_data, ground_fallback = await registry_client.fetch_project(
            project_id=credit_id,
            registry=registry
        )

        if ground_fallback:
            fallback_sources.append("ground")

        if not ground_data:
            logger.warning(f"Ground layer: Project {credit_id} not found in {registry}")
            return build_unverified_result(
                credit_id, project_url, registry, "Unknown",
                data_mode="fetch_failed",
                data_freshness="Registry unavailable"
            )

        # STEP 2: Satellite Layer - Fetch NDVI Time Series
        logger.info(f"[Satellite Layer] Fetching NDVI data for {credit_id}")
        gee_client = GEEClient()

        # Calculate date range
        start_date = f"{ground_data.vintage_year}-01-01"
        end_date = datetime.now().strftime('%Y-%m-%d')

        ndvi_timeseries, satellite_fallback = await gee_client.get_ndvi_timeseries(
            lat=ground_data.location.latitude,
            lon=ground_data.location.longitude,
            start_date=start_date,
            end_date=end_date,
            project_id=credit_id
        )

        if satellite_fallback:
            fallback_sources.append("satellite")

        if not ndvi_timeseries:
            logger.warning(f"Satellite layer: No NDVI data for {credit_id}")
            return build_unverified_result(
                credit_id, project_url, ground_data.registry, ground_data.project_type,
                data_mode="satellite_unavailable",
                data_freshness="No satellite coverage"
            )

        # STEP 3: AI Layer - Predict Carbon
        logger.info(f"[AI Layer] Running carbon estimation for {credit_id}")
        processor = NDVIProcessor()
        ndvi_avg = processor.calculate_average(ndvi_timeseries)

        estimator = CarbonEstimator()

        # Calculate project age
        project_age = datetime.now().year - ground_data.vintage_year

        # Estimate area from claimed carbon (rough heuristic: 10 tCO2/ha)
        estimated_area = ground_data.claimed_co2_tons / 10

        # Infer forest type from location (simplified)
        forest_type = _infer_forest_type(ground_data.location.latitude)

        ai_prediction = estimator.estimate(
            ndvi_avg=ndvi_avg,
            area_ha=estimated_area,
            forest_type=forest_type,
            age_years=project_age
        )

        # STEP 4: Scoring Layer - Calculate Trust Score
        logger.info(f"[Scoring Layer] Calculating trust score for {credit_id}")
        scorer = FraudScorer()

        result = scorer.calculate_trust_score(
            ground_data=ground_data,
            satellite_data=ndvi_timeseries,
            ai_prediction=ai_prediction
        )

        # Determine data mode
        fallback_used = len(fallback_sources) > 0
        if len(fallback_sources) == 0:
            data_mode = "live"
            data_freshness = "Real-time"
        elif len(fallback_sources) >= 2:
            data_mode = "cache"
            data_freshness = f"Cached ({', '.join(fallback_sources)} layers)"
        else:
            data_mode = "mixed"
            data_freshness = f"Mixed (cached: {', '.join(fallback_sources)})"

        # Get proper registry name
        registry_name = ground_data.registry

        # Convert to API response format (maintain existing contract)
        api_response = {
            "creditId": credit_id,
            "trustScore": result.trust_score,
            "verdict": result.verdict,
            "category": ground_data.project_type,
            "issuer": registry_name,
            "vintage": ground_data.vintage_year,
            "co2Equivalent": int(ground_data.claimed_co2_tons),
            "checks": [
                {
                    "name": check.name,
                    "passed": check.passed,
                    "score": check.score,
                    "description": check.evidence,
                    "evidence": f"Severity: {check.severity}"
                }
                for check in result.checks
            ],
            "fraudRisks": _generate_fraud_risks_from_checks(result.checks, result.trust_score),
            "verifiedAt": result.verified_at.isoformat(),
            "dataMode": data_mode,
            "fallbackUsed": fallback_used,
            "dataFreshness": data_freshness,
            "projectUrl": ground_data.registry_url
        }
        
        # Save to database
        try:
            await save_verification_to_db(
                api_response,
                json.dumps(ndvi_timeseries[0].model_dump() if ndvi_timeseries else {}, default=str),
                ground_data.project_type,
                ground_data.registry,
                ground_data.registry_url
            )
        except Exception as e:
            logger.warning(f"Failed to save verification to database: {e}")
        
        return api_response
        
    except Exception as e:
        logger.error(f"Verification engine error for {credit_id}: {e}", exc_info=True)
        return build_unverified_result(
            credit_id, project_url, registry, "Unknown",
            data_mode="engine_error",
            data_freshness=f"Error: {str(e)[:50]}"
        )


async def verify_bulk(credit_ids: list[str]) -> dict:
    """
    Verify multiple credits in parallel using asyncio.gather.
    Returns bulk verification result with sorted list (worst first).
    """
    # Process all credits in parallel
    tasks = [verify_single(credit_id) for credit_id in credit_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Separate successful results from errors
    successful_results = []
    errors = []
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append({
                "creditId": credit_ids[i],
                "error": str(result)
            })
        else:
            successful_results.append(result)
    
    # Sort by trust score ascending (worst first)
    successful_results.sort(key=lambda x: x["trustScore"])
    
    return {
        "results": successful_results,
        "totalSubmitted": len(credit_ids),
        "totalProcessed": len(successful_results),
        "totalErrors": len(errors),
        "errors": errors if errors else None
    }


def _infer_registry(credit_id: str) -> str:
    """Infer registry from credit ID format."""
    credit_id_upper = credit_id.upper()
    
    if "VCS-" in credit_id_upper or "VCS" in credit_id_upper:
        return "verra"
    elif "GOLD" in credit_id_upper or "GS" in credit_id_upper:
        return "gold_standard"
    elif "ACR-" in credit_id_upper or "ACR" in credit_id_upper:
        return "acr"
    else:
        return "verra"  # Default


def _build_project_url(credit_id: str, registry: str) -> Optional[str]:
    """Build project URL from credit ID and registry."""
    if registry == "verra":
        match = re.search(r'VCS-?(\d+)', credit_id, re.IGNORECASE)
        if match:
            number = match.group(1)
            return f"https://registry.verra.org/app/projectDetail/VCS/{number}"
    
    elif registry == "gold_standard":
        match = re.search(r'(\d+)', credit_id)
        if match:
            number = match.group(1)
            return f"https://registry.goldstandard.org/projects?q={number}"
    
    elif registry == "acr":
        return "https://acr2.apx.com/myModule/rpt/myrpt.asp?r=111"
    
    return None


def _infer_forest_type(latitude: float) -> str:
    """Infer forest type from latitude."""
    abs_lat = abs(latitude)
    
    if abs_lat < 23.5:  # Tropics
        return "tropical"
    elif abs_lat < 50:  # Temperate
        return "temperate"
    else:  # Boreal
        return "boreal"


def _generate_fraud_risks_from_checks(checks: list, trust_score: int) -> list:
    """Generate fraud risk warnings from check results."""
    risks = []
    
    # Aggregate failed checks
    failed_checks = [check for check in checks if not check.passed]
    
    if trust_score < 40 and trust_score > 0:
        risks.append({
            "category": "Low Trust Score",
            "severity": "high",
            "description": f"Credit failed {len(failed_checks)} verification checks",
            "evidence": f"Trust score {trust_score}/100 below acceptable threshold"
        })
    
    if trust_score < 70 and trust_score >= 40:
        risks.append({
            "category": "Moderate Risk",
            "severity": "medium",
            "description": "Some verification checks raised concerns",
            "evidence": "Further due diligence recommended before purchase"
        })
    
    # Add specific risks from failed checks
    for check in failed_checks:
        if check.severity in ["high", "critical"]:
            risks.append({
                "category": check.name,
                "severity": check.severity,
                "description": check.evidence,
                "evidence": f"Check score: {check.score}/25"
            })
    
    return risks


def build_unverified_result(
    credit_id: str, 
    project_url: Optional[str], 
    issuer: str, 
    category: str,
    data_mode: str = "fetch_failed",
    data_freshness: str = "Unavailable"
) -> dict:
    """
    Build UNVERIFIED result when fetch fails.
    No fake data - returns 0 score with fetch_failed status.
    """
    return {
        "creditId": credit_id,
        "trustScore": 0,
        "verdict": "UNVERIFIED",
        "category": category,
        "issuer": issuer,
        "vintage": 0,
        "co2Equivalent": 0,
        "checks": [
            {
                "name": "Registry Fetch",
                "passed": False,
                "score": 0,
                "description": "Unable to fetch data from external registry",
                "evidence": f"Could not retrieve data from {issuer}"
            }
        ],
        "fraudRisks": [
            {
                "category": "Data Unavailable",
                "severity": "high",
                "description": "Registry data could not be fetched - manual verification required",
                "evidence": f"External API request failed or was blocked"
            }
        ],
        "verifiedAt": datetime.utcnow().isoformat(),
        "dataMode": data_mode,
        "fallbackUsed": False,
        "dataFreshness": data_freshness,
        "projectUrl": project_url
    }


async def save_verification_to_db(result: dict, external_data: str, category: str, issuer: str, project_url: Optional[str]):
    """
    Save verification result to Supabase database.
    Saves to carbon_credits, trust_scores, and updates leaderboard_cache.
    """
    db_client = get_db_client()
    credit_id = result["creditId"]
    trust_score = result["trustScore"]
    verdict = result["verdict"]

    # Map category to project_type
    category_to_type = {
        "Renewable Energy": "renewable",
        "renewable": "renewable",
        "Forestry": "forestry",
        "forestry": "forestry",
        "Landfill Gas": "soil",
        "Methane": "other",
        "Soil Carbon": "soil",
        "soil": "soil",
        "Unknown": "other",
        "other": "other"
    }
    project_type = category_to_type.get(category, "other")

    # Create source snapshot hash for deterministic scoring
    source_hash = hashlib.sha256(external_data.encode()).hexdigest()[:16]

    # 1. Insert/Update carbon_credits
    try:
        carbon_credit_data = {
            "project_id": credit_id,
            "registry_name": issuer,
            "project_type": project_type,
            "claimed_tco2": result.get("co2Equivalent", 1000),
            "is_mandated": False,
            "vintage_year": result.get("vintage", 2023),
            "registry_url": project_url,
            "fetched_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        db_client.client.table("carbon_credits").upsert(
            carbon_credit_data,
            on_conflict="project_id"
        ).execute()

        logger.info(f"Saved carbon credit {credit_id} to database")
    except Exception as e:
        logger.error(f"Failed to save carbon_credit: {e}")

    # 2. Insert trust_scores
    try:
        checks_dict = {check["name"]: check["score"] for check in result["checks"]}

        trust_score_data = {
            "project_id": credit_id,
            "total_score": trust_score,
            "baseline_match_score": checks_dict.get("Carbon Overcrediting", 0),
            "additionality_score": checks_dict.get("Vegetation Health", 0),
            "permanence_risk_score": checks_dict.get("Vegetation Baseline", 0),
            "double_counting_score": checks_dict.get("Statistical Anomaly", 0),
            "verdict": verdict,
            "fallback_used": result.get("fallbackUsed", False),
            "data_mode": result.get("dataMode", "live"),
            "source_snapshot_hash": source_hash,
            "audit_trail": json.dumps({
                "checks": result["checks"],
                "fraud_risks": result["fraudRisks"],
                "verified_at": result["verifiedAt"]
            }, default=str),
            "computed_at": datetime.utcnow().isoformat()
        }

        db_client.client.table("trust_scores").insert(trust_score_data).execute()
        logger.info(f"Saved trust score for {credit_id} to database")

    except Exception as e:
        logger.error(f"Failed to save trust_score: {e}")

    # 3. Update leaderboard_cache
    try:
        rank_result = db_client.client.table("trust_scores").select(
            "total_score",
            count="exact"
        ).lt("total_score", trust_score).execute()

        rank = rank_result.count + 1 if rank_result.count else 1

        leaderboard_data = {
            "project_id": credit_id,
            "project_type": project_type,
            "total_score": trust_score,
            "verdict": verdict,
            "registry_name": issuer,
            "claimed_tco2": result.get("co2Equivalent", 1000),
            "rank_overall": rank,
            "rank_in_category": rank,
            "refreshed_at": datetime.utcnow().isoformat()
        }

        # Try to update leaderboard cache - handle missing UNIQUE constraint gracefully
        try:
            # Try upsert first (will work if UNIQUE constraint exists)
            db_client.client.table("leaderboard_cache").upsert(
                leaderboard_data,
                on_conflict="project_id"
            ).execute()
            logger.info(f"Updated leaderboard cache for {credit_id}")
        except Exception as upsert_error:
            if "unique" in str(upsert_error).lower() or "constraint" in str(upsert_error).lower():
                # UNIQUE constraint doesn't exist, try simple insert instead
                try:
                    db_client.client.table("leaderboard_cache").insert(leaderboard_data).execute()
                    logger.info(f"Inserted into leaderboard cache for {credit_id}")
                except Exception as insert_error:
                    logger.warning(f"Failed leaderboard cache update for {credit_id}: {insert_error}")
            else:
                logger.error(f"Failed to update leaderboard_cache: {upsert_error}")

    except Exception as e:
        logger.error(f"Error in leaderboard cache update process: {e}")
