"""
Leaderboard Router
Provides ranked list of most-flagged carbon credits.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db import get_db_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class LeaderboardEntry(BaseModel):
    creditId: str
    trustScore: int
    verdict: str
    category: str
    issuer: str
    flagCount: int
    lastVerified: str


@router.get("/leaderboard")
async def get_leaderboard(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Number of entries to return")
) -> List[LeaderboardEntry]:
    """
    Get leaderboard of most-flagged carbon credits from database.
    Sorted by trust score ascending (worst first).
    """

    try:
        db_client = get_db_client()

        # Query leaderboard_cache table
        query = db_client.client.table("leaderboard_cache").select("*")

        # Filter by category if provided
        if category:
            # Map frontend categories to database project_type
            category_map = {
                "Renewable Energy": "renewable",
                "Forestry": "forestry",
                "Landfill Gas": "soil",
                "Methane": "other",
                "Soil Carbon": "soil"
            }
            project_type = category_map.get(category, category.lower())
            query = query.eq("project_type", project_type)

        # Order by trust score ascending (worst first) and limit results
        result = query.order("total_score", desc=False).limit(limit).execute()

        if not result.data:
            logger.info("No leaderboard data found in database - returning empty list")
            return []

        # Transform database records to LeaderboardEntry format
        entries = []
        for row in result.data:
            # Calculate flag count from trust score (lower score = more flags)
            flag_count = max(0, int((100 - row["total_score"]) / 10))

            # Map project_type back to friendly category
            type_to_category = {
                "renewable": "Renewable Energy",
                "forestry": "Forestry",
                "soil": "Soil Carbon",
                "other": "Other"
            }

            entries.append(LeaderboardEntry(
                creditId=row["project_id"],
                trustScore=int(row["total_score"]),
                verdict=row["verdict"],
                category=type_to_category.get(row["project_type"], row["project_type"].title()),
                issuer=row["registry_name"],
                flagCount=flag_count,
                lastVerified=row["refreshed_at"]
            ))

        return entries

    except Exception as e:
        logger.error(f"Error fetching leaderboard: {e}")
        # Return empty list instead of failing
        return []
