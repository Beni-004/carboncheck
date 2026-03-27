"""
Scoring Formula Constants
Deterministic parameters for 4-component trust score computation.
These values are fixed to ensure repeatability and auditability.
"""

from typing import Literal

# ============================================================================
# SCORE COMPONENT WEIGHTS (each 0-25 points, total 0-100)
# ============================================================================

BASELINE_MATCH_MAX = 25.0
ADDITIONALITY_MAX = 25.0
PERMANENCE_RISK_MAX = 25.0
DOUBLE_COUNTING_MAX = 25.0

TOTAL_SCORE_MAX = 100.0

# ============================================================================
# BASELINE MATCH SCORING
# ============================================================================

# Fallback score when actual_grid_tco2 is unavailable (conservative middle)
BASELINE_MATCH_FALLBACK_SCORE = 12.5

# Minimum ratio threshold for full score
BASELINE_MATCH_PERFECT_RATIO = 1.0

# ============================================================================
# ADDITIONALITY SCORING
# ============================================================================

# Score if project is NOT mandated (true additionality)
ADDITIONALITY_TRUE_SCORE = 25.0

# Score if project IS mandated (no additionality)
ADDITIONALITY_FALSE_SCORE = 0.0

# ============================================================================
# PERMANENCE RISK SCORING
# ============================================================================

# Default scores by project type
PERMANENCE_RENEWABLE_DEFAULT = 20.0
PERMANENCE_OTHER_DEFAULT = 15.0
PERMANENCE_FORESTRY_FALLBACK = 10.0  # When fire risk unavailable

# Fire risk conversion factor (fire_risk_index 0-100 -> score reduction 0-25)
FIRE_RISK_PENALTY_FACTOR = 0.25

# Maximum fire risk penalty
FIRE_RISK_MAX_PENALTY = 25.0

# ============================================================================
# DOUBLE COUNTING SCORING
# ============================================================================

# Score if project appears in only one registry (unique)
DOUBLE_COUNTING_UNIQUE_SCORE = 25.0

# Score if project appears in multiple registries (likely double-counted)
DOUBLE_COUNTING_MULTIPLE_SCORE = 0.0

# Threshold for considering a project as double-counted
DOUBLE_COUNTING_THRESHOLD = 2

# ============================================================================
# VERDICT THRESHOLDS
# ============================================================================

# Total score thresholds for verdict assignment
VERDICT_FAIL_THRESHOLD = 40.0      # score < 40 = FAIL
VERDICT_WARNING_THRESHOLD = 70.0   # 40 <= score < 70 = WARNING
                                    # score >= 70 = PASS

VerdictType = Literal["FAIL", "WARNING", "PASS"]


def compute_verdict(total_score: float) -> VerdictType:
    """
    Compute verdict from total score using deterministic thresholds.
    
    Args:
        total_score: Total trust score (0-100)
    
    Returns:
        "FAIL", "WARNING", or "PASS"
    """
    if total_score < VERDICT_FAIL_THRESHOLD:
        return "FAIL"
    elif total_score < VERDICT_WARNING_THRESHOLD:
        return "WARNING"
    else:
        return "PASS"


# ============================================================================
# DATA MODE TRACKING
# ============================================================================

DataModeType = Literal["live", "cached", "partial"]

# Data mode classification rules:
# - "live": All sources returned fresh data
# - "cached": All sources used fallback cache
# - "partial": Mix of live and cached sources


def compute_data_mode(sources_used_cache: list[bool]) -> DataModeType:
    """
    Determine data mode from source cache usage flags.
    
    Args:
        sources_used_cache: List of boolean flags indicating cache usage per source
    
    Returns:
        "live", "cached", or "partial"
    """
    if not sources_used_cache:
        return "live"
    
    cache_count = sum(sources_used_cache)
    
    if cache_count == 0:
        return "live"
    elif cache_count == len(sources_used_cache):
        return "cached"
    else:
        return "partial"


# ============================================================================
# EXTERNAL API CONFIGURATION
# ============================================================================

# Fixed timeout for all external API calls (seconds)
# Increased to accommodate slower registry scraping and satellite data operations
EXTERNAL_API_TIMEOUT = 15.0

# Retry configuration (disabled for hackathon to prioritize fallback)
EXTERNAL_API_RETRIES = 0

# ============================================================================
# BULK VERIFICATION LIMITS
# ============================================================================

# Maximum number of project IDs in bulk verification request
BULK_VERIFY_MAX_IDS = 50

# Minimum number of IDs to qualify as bulk request
BULK_VERIFY_MIN_IDS = 2
