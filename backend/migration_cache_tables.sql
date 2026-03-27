-- CarbonCheck Cache Tables Migration
-- Run this SQL in your Supabase SQL Editor

-- =============================================================================
-- Create verification_cache table for storing fallback data
-- =============================================================================

CREATE TABLE IF NOT EXISTS verification_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    layer TEXT NOT NULL CHECK (layer IN ('ground', 'satellite', 'ai')),
    data JSONB NOT NULL,
    cached_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_verification_cache_project_layer
    ON verification_cache(project_id, layer, cached_at DESC);

CREATE INDEX IF NOT EXISTS idx_verification_cache_expires
    ON verification_cache(expires_at);

-- Create unique constraint to prevent duplicate cache entries
CREATE UNIQUE INDEX IF NOT EXISTS idx_verification_cache_unique
    ON verification_cache(project_id, layer);

-- Add comment
COMMENT ON TABLE verification_cache IS
    'Cached verification data for fallback when external APIs timeout';


-- =============================================================================
-- Create leaderboard_cache table for pre-computed rankings
-- =============================================================================

CREATE TABLE IF NOT EXISTS leaderboard_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id TEXT NOT NULL,
    project_type TEXT NOT NULL CHECK (project_type IN ('forestry', 'renewable', 'soil', 'other')),
    trust_score NUMERIC(5,2) NOT NULL CHECK (trust_score >= 0 AND trust_score <= 100),
    verdict TEXT NOT NULL CHECK (verdict IN ('FAIL', 'WARNING', 'PASS', 'UNVERIFIED')),
    registry_name TEXT,
    claimed_tco2 NUMERIC(14,2),
    rank_overall INT NOT NULL,
    rank_in_category INT NOT NULL,
    cached_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_leaderboard_cache_rank
    ON leaderboard_cache(rank_overall, cached_at DESC);

CREATE INDEX IF NOT EXISTS idx_leaderboard_cache_category
    ON leaderboard_cache(project_type, rank_in_category, cached_at DESC);

-- Add comment
COMMENT ON TABLE leaderboard_cache IS
    'Pre-computed leaderboard rankings for fast public access';
