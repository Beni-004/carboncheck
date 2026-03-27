"""
Database client and connection management for Supabase Postgres.
Provides async connection pooling and query helpers.
"""

import os
from typing import Optional
from pathlib import Path
from supabase import create_client, Client
import logging

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


class DatabaseClient:
    """
    Supabase database client wrapper with connection management.
    Singleton pattern to reuse client across requests.
    """
    
    _instance: Optional["DatabaseClient"] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client from environment variables."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Missing required environment variables: SUPABASE_URL, SUPABASE_SERVICE_KEY"
            )
        
        self._client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully")
    
    @property
    def client(self) -> Client:
        """Get Supabase client instance."""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def health_check(self) -> bool:
        """
        Check database connectivity.
        Returns True if connected, False otherwise.
        """
        try:
            # Simple query to verify connection
            result = self.client.table("carbon_credits").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database client instance
db_client = DatabaseClient()


def get_db_client() -> DatabaseClient:
    """
    Dependency injection helper for FastAPI routes.
    Returns the global database client instance.
    """
    return db_client
