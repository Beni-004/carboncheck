"""
Carbon estimation from satellite observations.
Based on: carbonplan/forest-offsets
"""
import numpy as np
from typing import Tuple
from pydantic import BaseModel


class CarbonEstimate(BaseModel):
    """Carbon estimation result."""
    co2_tons: float
    confidence_interval_low: float
    confidence_interval_high: float
    uncertainty_pct: float


class CarbonEstimator:
    """
    Estimate carbon sequestration from NDVI data.
    
    Uses simplified allometric equations:
    NDVI → Biomass → Carbon → CO2
    
    Reference:
    - CarbonPlan: https://github.com/carbonplan/forest-offsets
    - Literature: Foody et al. (2003), Remote Sensing of Environment
    """
    
    # Allometric coefficients (from literature)
    NDVI_TO_BIOMASS_COEF = 150.0  # tons biomass per hectare per NDVI unit
    BIOMASS_TO_CARBON = 0.47  # Carbon fraction in biomass
    CARBON_TO_CO2 = 3.67  # Molecular weight ratio CO2/C
    
    # Uncertainty factors
    BASE_UNCERTAINTY = 0.30  # ±30% base uncertainty
    
    def estimate(
        self,
        ndvi_avg: float,
        area_ha: float,
        forest_type: str = "tropical",
        age_years: int = 10
    ) -> CarbonEstimate:
        """
        Estimate carbon stock from NDVI.
        
        Args:
            ndvi_avg: Average NDVI over project area
            area_ha: Project area in hectares
            forest_type: Forest type ("tropical", "temperate", "boreal")
            age_years: Years since project start
        
        Returns:
            CarbonEstimate with CO2 tons and uncertainty
        """
        # Step 1: NDVI → Biomass
        biomass_per_ha = self._ndvi_to_biomass(ndvi_avg, forest_type)
        
        # Step 2: Account for forest age (growth curve)
        growth_factor = self._age_growth_factor(age_years, forest_type)
        biomass_per_ha *= growth_factor
        
        # Step 3: Total biomass
        total_biomass = biomass_per_ha * area_ha
        
        # Step 4: Biomass → Carbon
        total_carbon = total_biomass * self.BIOMASS_TO_CARBON
        
        # Step 5: Carbon → CO2
        total_co2 = total_carbon * self.CARBON_TO_CO2
        
        # Step 6: Calculate uncertainty
        uncertainty = self._calculate_uncertainty(
            ndvi_avg, area_ha, forest_type, age_years
        )
        
        return CarbonEstimate(
            co2_tons=total_co2,
            confidence_interval_low=total_co2 * (1 - uncertainty),
            confidence_interval_high=total_co2 * (1 + uncertainty),
            uncertainty_pct=uncertainty * 100
        )
    
    def _ndvi_to_biomass(self, ndvi: float, forest_type: str) -> float:
        """Convert NDVI to biomass per hectare."""
        coef_multipliers = {
            "tropical": 1.2,
            "temperate": 1.0,
            "boreal": 0.7,
        }
        
        multiplier = coef_multipliers.get(forest_type, 1.0)
        biomass = ndvi * self.NDVI_TO_BIOMASS_COEF * multiplier
        
        # Clamp to realistic range
        return max(0, min(biomass, 500))
    
    def _age_growth_factor(self, age_years: int, forest_type: str) -> float:
        """
        Growth curve factor based on forest age.
        Young forests accumulate carbon faster.
        """
        max_age = {"tropical": 40, "temperate": 60, "boreal": 80}
        k = max_age.get(forest_type, 50)
        
        # Logistic function
        factor = 1 / (1 + np.exp(-0.1 * (age_years - k/2)))
        
        return float(factor)
    
    def _calculate_uncertainty(
        self,
        ndvi: float,
        area_ha: float,
        forest_type: str,
        age_years: int
    ) -> float:
        """
        Calculate uncertainty in carbon estimate.
        
        Higher uncertainty for:
        - Low NDVI (sparse vegetation)
        - Large areas (scaling errors)
        - Young forests (growth variability)
        """
        uncertainty = self.BASE_UNCERTAINTY
        
        # Increase uncertainty for low NDVI
        if ndvi < 0.4:
            uncertainty += 0.10
        
        # Increase uncertainty for large areas
        if area_ha > 10000:
            uncertainty += 0.05
        
        # Increase uncertainty for young forests
        if age_years < 5:
            uncertainty += 0.10
        
        return min(uncertainty, 0.60)
