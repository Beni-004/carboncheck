-- CarbonCheck Initial Schema Migration
-- Tables: carbon_credits, trust_scores, leaderboard_cache
-- Purpose: Rigid schema for credit verification, scoring, and public leaderboard

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Ensure we're working in the public schema
SET search_path TO public;

-- Drop existing tables if they exist (CASCADE will drop triggers and dependencies)
DROP TABLE IF EXISTS leaderboard_cache CASCADE;
DROP TABLE IF EXISTS trust_scores CASCADE;
DROP TABLE IF EXISTS carbon_credits CASCADE;

-- Drop existing functions if they exist
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Table: carbon_credits
-- Stores registry credit data with provenance tracking
CREATE TABLE carbon_credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id TEXT NOT NULL UNIQUE,
    registry_name TEXT NOT NULL,
    project_type TEXT NOT NULL CHECK (project_type IN ('forestry', 'renewable', 'soil', 'other')),
    claimed_tco2 NUMERIC(12, 2) NOT NULL CHECK (claimed_tco2 >= 0),
    is_mandated BOOLEAN NOT NULL DEFAULT FALSE,
    location TEXT,
    vintage_year INTEGER,
    registry_url TEXT,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_carbon_credits_project_id ON carbon_credits(project_id);
CREATE INDEX idx_carbon_credits_project_type ON carbon_credits(project_type);
CREATE INDEX idx_carbon_credits_fetched_at ON carbon_credits(fetched_at);

-- Table: trust_scores
-- Stores computed trust scores with 4-component breakdown and audit trail
CREATE TABLE trust_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id TEXT NOT NULL,
    total_score NUMERIC(5, 2) NOT NULL CHECK (total_score >= 0 AND total_score <= 100),
    baseline_match_score NUMERIC(5, 2) NOT NULL CHECK (baseline_match_score >= 0 AND baseline_match_score <= 25),
    additionality_score NUMERIC(5, 2) NOT NULL CHECK (additionality_score >= 0 AND additionality_score <= 25),
    permanence_risk_score NUMERIC(5, 2) NOT NULL CHECK (permanence_risk_score >= 0 AND permanence_risk_score <= 25),
    double_counting_score NUMERIC(5, 2) NOT NULL CHECK (double_counting_score >= 0 AND double_counting_score <= 25),
    verdict TEXT NOT NULL CHECK (verdict IN ('FAIL', 'WARNING', 'PASS')),
    fallback_used BOOLEAN NOT NULL DEFAULT FALSE,
    data_mode TEXT NOT NULL CHECK (data_mode IN ('live', 'cached', 'partial')),
    source_snapshot_hash TEXT NOT NULL,
    audit_trail JSONB NOT NULL,
    rank_in_batch INTEGER,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_trust_scores_project_id ON trust_scores(project_id);
CREATE INDEX idx_trust_scores_total_score ON trust_scores(total_score DESC);
CREATE INDEX idx_trust_scores_verdict ON trust_scores(verdict);
CREATE INDEX idx_trust_scores_computed_at ON trust_scores(computed_at DESC);

-- Table: leaderboard_cache
-- Materialized view for public leaderboard with category filtering
CREATE TABLE leaderboard_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id TEXT NOT NULL,
    project_type TEXT NOT NULL CHECK (project_type IN ('forestry', 'renewable', 'soil', 'other')),
    total_score NUMERIC(5, 2) NOT NULL CHECK (total_score >= 0 AND total_score <= 100),
    verdict TEXT NOT NULL CHECK (verdict IN ('FAIL', 'WARNING', 'PASS')),
    registry_name TEXT NOT NULL,
    claimed_tco2 NUMERIC(12, 2) NOT NULL,
    rank_overall INTEGER NOT NULL,
    rank_in_category INTEGER NOT NULL,
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_leaderboard_cache_project_type ON leaderboard_cache(project_type);
CREATE INDEX idx_leaderboard_cache_rank_overall ON leaderboard_cache(rank_overall);
CREATE INDEX idx_leaderboard_cache_rank_in_category ON leaderboard_cache(rank_in_category);
CREATE INDEX idx_leaderboard_cache_refreshed_at ON leaderboard_cache(refreshed_at DESC);

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update updated_at on carbon_credits
CREATE TRIGGER update_carbon_credits_updated_at
    BEFORE UPDATE ON carbon_credits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE carbon_credits IS 'Registry credit data with provenance tracking';
COMMENT ON TABLE trust_scores IS '4-component trust scores with audit trail and fallback tracking';
COMMENT ON TABLE leaderboard_cache IS 'Materialized public leaderboard with category rankings';

COMMENT ON COLUMN trust_scores.fallback_used IS 'TRUE if any source used cached data due to timeout/failure';
COMMENT ON COLUMN trust_scores.data_mode IS 'live=all fresh, cached=all cached, partial=mixed';
COMMENT ON COLUMN trust_scores.source_snapshot_hash IS 'Deterministic hash of source data for repeatability';
COMMENT ON COLUMN trust_scores.rank_in_batch IS 'Rank within bulk verification batch (NULL for single verify)';
