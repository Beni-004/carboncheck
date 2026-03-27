"""
Database migration for verification cache table.
Supports fallback data storage when external APIs timeout.
"""

from supabase import create_client, Client
import os
from datetime import datetime

# Supabase connection
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def create_verification_cache_table():
    """
    Create verification_cache table for storing fallback data.

    Schema:
    - id: UUID primary key
    - project_id: Carbon credit project ID
    - layer: ground | satellite | ai
    - data: JSONB data payload
    - cached_at: Timestamp when cached
    - expires_at: Expiration timestamp (24h default)
    """

    sql = """
    -- Create verification_cache table
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
    """

    print("Creating verification_cache table...")

    # Note: Supabase Python client doesn't support direct SQL execution
    # This SQL should be run via Supabase Dashboard or SQL editor
    print("\n" + "="*80)
    print("IMPORTANT: Run the following SQL in your Supabase SQL Editor:")
    print("="*80)
    print(sql)
    print("="*80 + "\n")

    return sql


def create_leaderboard_cache_table():
    """
    Create leaderboard_cache table for pre-computed leaderboard rankings.
    """

    sql = """
    -- Create leaderboard_cache table
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
    """

    print("Creating leaderboard_cache table...")
    print("\n" + "="*80)
    print("IMPORTANT: Run the following SQL in your Supabase SQL Editor:")
    print("="*80)
    print(sql)
    print("="*80 + "\n")

    return sql


if __name__ == "__main__":
    print("CarbonCheck Database Migration - Cache Tables")
    print("=" * 80)
    print()

    cache_sql = create_verification_cache_table()
    print()
    leaderboard_sql = create_leaderboard_cache_table()

    print("\n" + "="*80)
    print("Migration SQL generated successfully!")
    print("Please copy the SQL above and run it in your Supabase SQL Editor.")
    print("="*80)

    # Save to file for reference
    with open("migration_cache_tables.sql", "w") as f:
        f.write("-- CarbonCheck Cache Tables Migration\n")
        f.write("-- Generated: " + datetime.now().isoformat() + "\n\n")
        f.write(cache_sql)
        f.write("\n\n")
        f.write(leaderboard_sql)

    print("\nSQL also saved to: migration_cache_tables.sql")
