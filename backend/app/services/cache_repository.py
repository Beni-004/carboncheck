"""
Cache Repository for Verification Data.
Provides fallback data when external APIs are unavailable.
"""

import json
import logging
from typing import Optional, Any, List
from datetime import datetime, timedelta
from app.db import get_db_client

logger = logging.getLogger(__name__)


class CacheRepository:
    """
    Manages cached verification data for fallback scenarios.

    Cache TTL: 24 hours (configurable via env)
    Storage: Supabase verification_cache table
    """

    def __init__(self, ttl_seconds: int = 86400):
        """
        Initialize cache repository.

        Args:
            ttl_seconds: Cache time-to-live in seconds (default: 24 hours)
        """
        self.ttl_seconds = ttl_seconds
        self.db = get_db_client()

    async def get_cached_ground_data(self, project_id: str) -> Optional[dict]:
        """
        Retrieve cached ground layer data for a project.

        Args:
            project_id: Carbon credit project ID

        Returns:
            Cached data dict or None if not found/expired
        """
        try:
            result = self.db.client.table("verification_cache").select("*").eq(
                "project_id", project_id
            ).eq(
                "layer", "ground"
            ).order(
                "cached_at", desc=True
            ).limit(1).execute()

            if not result.data or len(result.data) == 0:
                logger.debug(f"No ground cache found for {project_id}")
                return None

            cache_entry = result.data[0]
            cached_at = datetime.fromisoformat(cache_entry["cached_at"].replace("Z", "+00:00"))
            age_seconds = (datetime.now(cached_at.tzinfo) - cached_at).total_seconds()

            if age_seconds > self.ttl_seconds:
                logger.info(f"Ground cache expired for {project_id} (age: {age_seconds}s)")
                return None

            logger.info(f"Using ground cache for {project_id} (age: {age_seconds}s)")
            return json.loads(cache_entry["data"])

        except Exception as e:
            logger.error(f"Failed to retrieve ground cache for {project_id}: {e}")
            return None

    async def save_ground_data(self, project_id: str, data: dict) -> bool:
        """
        Save ground layer data to cache.

        Args:
            project_id: Carbon credit project ID
            data: Ground layer data to cache

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            cache_entry = {
                "project_id": project_id,
                "layer": "ground",
                "data": json.dumps(data, default=str),  # Convert datetime objects to strings
                "cached_at": datetime.utcnow().isoformat() + "Z"
            }

            self.db.client.table("verification_cache").upsert(
                cache_entry, on_conflict="project_id,layer"
            ).execute()
            logger.info(f"Saved ground cache for {project_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save ground cache for {project_id}: {e}")
            return False

    async def get_cached_satellite_data(self, project_id: str) -> Optional[List[dict]]:
        """
        Retrieve cached satellite NDVI data for a project.

        Args:
            project_id: Carbon credit project ID

        Returns:
            Cached NDVI time series or None if not found/expired
        """
        try:
            result = self.db.client.table("verification_cache").select("*").eq(
                "project_id", project_id
            ).eq(
                "layer", "satellite"
            ).order(
                "cached_at", desc=True
            ).limit(1).execute()

            if not result.data or len(result.data) == 0:
                logger.debug(f"No satellite cache found for {project_id}")
                return None

            cache_entry = result.data[0]
            cached_at = datetime.fromisoformat(cache_entry["cached_at"].replace("Z", "+00:00"))
            age_seconds = (datetime.now(cached_at.tzinfo) - cached_at).total_seconds()

            if age_seconds > self.ttl_seconds:
                logger.info(f"Satellite cache expired for {project_id} (age: {age_seconds}s)")
                return None

            logger.info(f"Using satellite cache for {project_id} (age: {age_seconds}s)")
            return json.loads(cache_entry["data"])

        except Exception as e:
            logger.error(f"Failed to retrieve satellite cache for {project_id}: {e}")
            return None

    async def save_satellite_data(self, project_id: str, ndvi_data: List[dict]) -> bool:
        """
        Save satellite NDVI data to cache.

        Args:
            project_id: Carbon credit project ID
            ndvi_data: NDVI time series data to cache

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            cache_entry = {
                "project_id": project_id,
                "layer": "satellite",
                "data": json.dumps(ndvi_data, default=str),  # Convert datetime objects to strings
                "cached_at": datetime.utcnow().isoformat() + "Z"
            }

            self.db.client.table("verification_cache").upsert(
                cache_entry, on_conflict="project_id,layer"
            ).execute()
            logger.info(f"Saved satellite cache for {project_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save satellite cache for {project_id}: {e}")
            return False

    async def get_recent_verifications(
        self,
        limit: int = 100,
        project_type: Optional[str] = None
    ) -> List[dict]:
        """
        Retrieve recent verification results for leaderboard.

        Args:
            limit: Maximum number of results
            project_type: Optional filter by project type

        Returns:
            List of recent verification results
        """
        try:
            query = self.db.client.table("trust_scores").select("*")

            if project_type:
                query = query.eq("category", project_type)

            result = query.order("verified_at", desc=True).limit(limit).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to retrieve recent verifications: {e}")
            return []

    async def clear_expired_cache(self) -> int:
        """
        Remove cache entries older than TTL.

        Returns:
            Number of entries deleted
        """
        try:
            cutoff = datetime.utcnow() - timedelta(seconds=self.ttl_seconds)
            cutoff_iso = cutoff.isoformat()

            result = self.db.client.table("verification_cache").delete().lt(
                "cached_at", cutoff_iso
            ).execute()

            count = len(result.data) if result.data else 0
            logger.info(f"Cleared {count} expired cache entries")
            return count

        except Exception as e:
            logger.error(f"Failed to clear expired cache: {e}")
            return 0
