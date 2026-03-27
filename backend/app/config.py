"""
Application configuration management.
Loads environment variables and provides typed config access.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Supabase
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_service_key: str = Field(..., env="SUPABASE_SERVICE_KEY")
    
    # API
    api_title: str = "CarbonCheck API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api"
    
    # External API Timeouts (seconds)
    # Increased to accommodate slower registry scraping and satellite data operations
    external_api_timeout: int = 15
    
    # Bulk verification limits
    bulk_verify_max_ids: int = 50
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Dependency injection helper for FastAPI routes.
    Returns the global settings instance.
    """
    return settings
