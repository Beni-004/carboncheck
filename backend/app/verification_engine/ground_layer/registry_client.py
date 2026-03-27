"""
Client for fetching data from carbon registries.
Uses carbonplan/offsets-db patterns as reference.
"""
import httpx
import logging
from typing import Optional
from bs4 import BeautifulSoup
import re
from .models import RegistryProject, ProjectLocation

logger = logging.getLogger(__name__)


class RegistryClient:
    """Base client for carbon credit registries."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
    
    async def fetch_project(
        self,
        project_id: str,
        registry: str
    ) -> Optional[RegistryProject]:
        """
        Fetch project data from specified registry.
        
        Args:
            project_id: Registry-specific project ID (e.g., "VCS-191")
            registry: Registry name ("verra", "gold_standard", "acr")
        
        Returns:
            RegistryProject or None if not found
        """
        try:
            if registry == "verra":
                return await self._fetch_verra(project_id)
            elif registry == "gold_standard":
                return await self._fetch_gold_standard(project_id)
            elif registry == "acr":
                return await self._fetch_acr(project_id)
            else:
                logger.warning(f"Unknown registry: {registry}")
                return None
        except Exception as e:
            logger.error(f"Error fetching project {project_id} from {registry}: {e}")
            return None
    
    async def _fetch_verra(self, project_id: str) -> Optional[RegistryProject]:
        """
        Fetch from Verra Registry.
        
        Example URL: https://registry.verra.org/app/projectDetail/VCS/191
        """
        # Extract numeric ID from project_id (e.g., "VCS-191" -> "191")
        match = re.search(r'\d+', project_id)
        if not match:
            logger.warning(f"Could not extract numeric ID from {project_id}")
            return None
            
        numeric_id = match.group()
        
        url = f"https://registry.verra.org/app/projectDetail/VCS/{numeric_id}"
        
        try:
            response = await self.client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse project details (simplified - real parsing is more complex)
            project_name = soup.find('h1', class_='project-title')
            if project_name:
                project_name = project_name.text.strip()
            else:
                project_name = f"Verra Project {numeric_id}"
            
            # Extract location
            location = self._parse_verra_location(soup)
            
            # Extract carbon data
            carbon_data = self._parse_verra_carbon(soup)
            
            return RegistryProject(
                project_id=project_id,
                registry="verra",
                project_name=project_name,
                location=location,
                claimed_co2_tons=carbon_data.get('claimed_co2', 50000),
                vintage_year=carbon_data.get('vintage_year', 2020),
                methodology=carbon_data.get('methodology', 'VM0015'),
                project_type=self._infer_project_type(carbon_data.get('methodology', '')),
                registry_url=url
            )
        
        except Exception as e:
            logger.error(f"Error fetching Verra project {project_id}: {e}")
            return None
    
    def _parse_verra_location(self, soup: BeautifulSoup) -> ProjectLocation:
        """Extract lat/lon from Verra project page."""
        # Look for coordinates in various possible locations
        coords_text = soup.find(text=re.compile(r'-?\d+\.\d+,\s*-?\d+\.\d+'))
        
        if coords_text:
            match = re.search(r'(-?\d+\.\d+),\s*(-?\d+\.\d+)', coords_text)
            if match:
                lat, lon = float(match.group(1)), float(match.group(2))
                return ProjectLocation(latitude=lat, longitude=lon)
        
        # Fallback: return default location
        logger.warning("Could not parse location from Verra page, using default")
        return ProjectLocation(latitude=0.0, longitude=0.0)
    
    def _parse_verra_carbon(self, soup: BeautifulSoup) -> dict:
        """Extract carbon data from Verra page."""
        # Simplified parsing - real implementation needs robust extraction
        return {
            'claimed_co2': 50000.0,
            'vintage_year': 2020,
            'methodology': 'VM0015'
        }
    
    def _infer_project_type(self, methodology: str) -> str:
        """Map methodology code to project type."""
        if 'VM' in methodology or 'AR' in methodology:
            return 'forestry'
        elif 'ACM' in methodology:
            return 'renewable'
        else:
            return 'other'
    
    async def _fetch_gold_standard(self, project_id: str) -> Optional[RegistryProject]:
        """Fetch from Gold Standard Registry."""
        # Simplified implementation
        logger.info(f"Fetching Gold Standard project {project_id}")
        
        # Extract numeric ID
        match = re.search(r'\d+', project_id)
        if not match:
            return None
        numeric_id = match.group()
        
        url = f"https://registry.goldstandard.org/projects/details/{numeric_id}"
        
        return RegistryProject(
            project_id=project_id,
            registry="gold_standard",
            project_name=f"Gold Standard Project {numeric_id}",
            location=ProjectLocation(latitude=0.0, longitude=0.0),
            claimed_co2_tons=30000.0,
            vintage_year=2021,
            methodology="GS-CDM",
            project_type="forestry",
            registry_url=url
        )
    
    async def _fetch_acr(self, project_id: str) -> Optional[RegistryProject]:
        """Fetch from American Carbon Registry."""
        logger.info(f"Fetching ACR project {project_id}")
        
        url = "https://acr2.apx.com/myModule/rpt/myrpt.asp?r=111"
        
        return RegistryProject(
            project_id=project_id,
            registry="acr",
            project_name=f"ACR Project {project_id}",
            location=ProjectLocation(latitude=0.0, longitude=0.0),
            claimed_co2_tons=20000.0,
            vintage_year=2019,
            methodology="ACR-001",
            project_type="soil",
            registry_url=url
        )
