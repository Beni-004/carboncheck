"""
Integration Layer Configuration
Connects FastAPI CarbonCheck system with UNDP Registry Service
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class IntegrationSettings(BaseSettings):
    """
    Settings for the integration layer between CarbonCheck and UNDP Registry.
    """

    # UNDP Registry Service Connection
    registry_service_url: str = Field(
        default="http://localhost:3001",
        env="REGISTRY_SERVICE_URL"
    )
    registry_api_prefix: str = "/api/v1"
    registry_timeout: int = Field(default=30, env="REGISTRY_TIMEOUT")

    # CarbonCheck Database (Supabase)
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_service_key: str = Field(..., env="SUPABASE_SERVICE_KEY")

    # Sentinel Hub API Configuration (replaces GEE)
    satellite_api_enabled: bool = Field(default=True, env="SATELLITE_API_ENABLED")
    sentinel_client_id: Optional[str] = Field(default=None, env="SENTINEL_CLIENT_ID")
    sentinel_client_secret: Optional[str] = Field(default=None, env="SENTINEL_CLIENT_SECRET")
    sentinel_api_url: str = Field(
        default="https://sh.dataspace.copernicus.eu/api/v1/process",
        env="SENTINEL_API_URL"
    )

    # Feature Flags
    enable_auto_verification: bool = Field(default=False, env="ENABLE_AUTO_VERIFICATION")
    enable_registry_sync: bool = Field(default=True, env="ENABLE_REGISTRY_SYNC")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
integration_settings = IntegrationSettings()


def get_integration_settings() -> IntegrationSettings:
    """
    Dependency injection helper for FastAPI routes.
    """
    return integration_settings
