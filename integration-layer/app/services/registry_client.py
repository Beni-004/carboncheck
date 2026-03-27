"""
Registry Service Client
HTTP client for communicating with the UNDP Registry NestJS service.
"""

import httpx
import logging
from typing import Optional, List, Dict, Any
from ..config import integration_settings
from ..models.registry_models import (
    RegistryProgramme,
    RegistryStatistics,
    RegistryProjectQuery,
)

logger = logging.getLogger(__name__)


class RegistryServiceClient:
    """
    HTTP client for the UNDP Registry Service.
    Provides async methods to interact with the registry API.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or integration_settings.registry_service_url
        self.api_prefix = integration_settings.registry_api_prefix
        self.timeout = integration_settings.registry_timeout

    @property
    def _full_url(self) -> str:
        return f"{self.base_url}{self.api_prefix}"

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request to the registry service"""
        url = f"{self._full_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Registry API error: {e.response.status_code} - {e.response.text}")
                raise RegistryServiceError(
                    f"Registry service returned {e.response.status_code}",
                    status_code=e.response.status_code,
                )
            except httpx.RequestError as e:
                logger.error(f"Registry connection error: {str(e)}")
                raise RegistryServiceError(f"Failed to connect to registry: {str(e)}")

    # ============== Programme Endpoints ==============

    async def get_programmes(
        self,
        query: Optional[RegistryProjectQuery] = None,
    ) -> Dict[str, Any]:
        """Get list of programmes with optional filters"""
        params = {}
        if query:
            params = {
                k: v for k, v in query.model_dump().items() if v is not None
            }
        return await self._request("GET", "/programmes", params=params)

    async def get_programme(self, programme_id: str) -> RegistryProgramme:
        """Get a specific programme by ID"""
        data = await self._request("GET", f"/programmes/{programme_id}")
        return RegistryProgramme(**data)

    async def get_programme_by_external_id(self, external_id: str) -> Optional[RegistryProgramme]:
        """Get a programme by external ID"""
        try:
            data = await self._request("GET", f"/programmes/external/{external_id}")
            return RegistryProgramme(**data) if data else None
        except RegistryServiceError as e:
            if e.status_code == 404:
                return None
            raise

    async def create_programme(self, programme_data: Dict[str, Any]) -> RegistryProgramme:
        """Create a new programme"""
        data = await self._request("POST", "/programmes", json_data=programme_data)
        return RegistryProgramme(**data)

    async def update_programme(
        self,
        programme_id: str,
        update_data: Dict[str, Any],
    ) -> RegistryProgramme:
        """Update an existing programme"""
        data = await self._request(
            "PUT",
            f"/programmes/{programme_id}",
            json_data=update_data,
        )
        return RegistryProgramme(**data)

    async def authorize_programme(self, programme_id: str) -> RegistryProgramme:
        """Authorize a programme"""
        data = await self._request("POST", f"/programmes/{programme_id}/authorize")
        return RegistryProgramme(**data)

    async def reject_programme(
        self,
        programme_id: str,
        reason: Optional[str] = None,
    ) -> RegistryProgramme:
        """Reject a programme"""
        json_data = {"reason": reason} if reason else {}
        data = await self._request(
            "POST",
            f"/programmes/{programme_id}/reject",
            json_data=json_data,
        )
        return RegistryProgramme(**data)

    # ============== Credit Operations ==============

    async def issue_credits(
        self,
        programme_id: str,
        credit_amount: float,
        comment: Optional[str] = None,
    ) -> RegistryProgramme:
        """Issue credits to a programme"""
        data = await self._request(
            "POST",
            "/programmes/credits/issue",
            json_data={
                "programmeId": programme_id,
                "creditAmount": credit_amount,
                "comment": comment,
            },
        )
        return RegistryProgramme(**data)

    async def transfer_credits(
        self,
        programme_id: str,
        from_company_id: int,
        to_company_id: int,
        credit_amount: float,
        comment: Optional[str] = None,
    ) -> RegistryProgramme:
        """Transfer credits between companies"""
        data = await self._request(
            "POST",
            "/programmes/credits/transfer",
            json_data={
                "programmeId": programme_id,
                "fromCompanyId": from_company_id,
                "toCompanyId": to_company_id,
                "creditAmount": credit_amount,
                "comment": comment,
            },
        )
        return RegistryProgramme(**data)

    async def retire_credits(
        self,
        programme_id: str,
        company_id: int,
        credit_amount: float,
        retirement_type: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> RegistryProgramme:
        """Retire credits"""
        data = await self._request(
            "POST",
            "/programmes/credits/retire",
            json_data={
                "programmeId": programme_id,
                "companyId": company_id,
                "creditAmount": credit_amount,
                "retirementType": retirement_type,
                "comment": comment,
            },
        )
        return RegistryProgramme(**data)

    # ============== Statistics ==============

    async def get_statistics(self) -> RegistryStatistics:
        """Get registry statistics"""
        data = await self._request("GET", "/programmes/statistics")
        return RegistryStatistics(**data)

    # ============== Health Check ==============

    async def health_check(self) -> bool:
        """Check if registry service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/v1/programmes?size=1")
                return response.status_code == 200
        except Exception:
            return False


class RegistryServiceError(Exception):
    """Custom exception for registry service errors"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


# Singleton instance
registry_client = RegistryServiceClient()


def get_registry_client() -> RegistryServiceClient:
    """Dependency injection helper"""
    return registry_client
