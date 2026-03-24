"""
Leaderboard Router
Provides ranked list of most-flagged carbon credits.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random

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
    Get leaderboard of most-flagged carbon credits.
    Sorted by flag count descending (worst first).
    """
    
    categories = ["Renewable Energy", "Forestry", "Landfill Gas", "Methane", "Soil Carbon"]
    issuers = [
        "Verified Carbon Standard",
        "Gold Standard",
        "American Carbon Registry",
        "Climate Action Reserve"
    ]
    
    # Generate mock leaderboard entries
    entries = []
    for i in range(100):
        score = random.randint(0, 100)
        cat = random.choice(categories)
        
        entry = LeaderboardEntry(
            creditId=f"{cat[:3].upper()}-{2020 + i // 20}-{str(i + 1).zfill(3)}",
            trustScore=score,
            verdict="PASS" if score > 70 else "WARNING" if score > 40 else "FAIL",
            category=cat,
            issuer=random.choice(issuers),
            flagCount=(100 - score) // 10 + random.randint(0, 5),
            lastVerified=(datetime.utcnow() - timedelta(
                days=random.randint(0, 7)
            )).isoformat()
        )
        entries.append(entry)
    
    # Filter by category if provided
    if category:
        entries = [e for e in entries if e.category == category]
    
    # Sort by flag count descending (most flagged first)
    entries.sort(key=lambda x: x.flagCount, reverse=True)
    
    # Return limited results
    return entries[:limit]
