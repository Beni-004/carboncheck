#!/usr/bin/env python3
"""
Apply database migration manually.
"""

import os
import sys
sys.path.append('/home/iyad/Projects/carboncheck/backend')

from app.db import get_db_client

def apply_migration():
    """Apply the database migration."""
    client = get_db_client()

    # SQL to create verification_cache table
    create_verification_cache = """
    CREATE TABLE IF NOT EXISTS verification_cache (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        project_id TEXT NOT NULL,
        layer TEXT NOT NULL CHECK (layer IN ('ground', 'satellite')),
        data JSONB NOT NULL,
        cached_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(project_id, layer)
    );
    """

    # SQL to add indexes
    create_indexes = """
    CREATE INDEX IF NOT EXISTS idx_verification_cache_project_id ON verification_cache(project_id);
    CREATE INDEX IF NOT EXISTS idx_verification_cache_layer ON verification_cache(layer);
    CREATE INDEX IF NOT EXISTS idx_verification_cache_cached_at ON verification_cache(cached_at DESC);
    """

    # SQL to add UNIQUE constraint to leaderboard_cache
    # First drop the table and recreate with the constraint
    fix_leaderboard_cache = """
    -- Drop and recreate leaderboard_cache with UNIQUE constraint
    DROP TABLE IF EXISTS leaderboard_cache CASCADE;

    CREATE TABLE leaderboard_cache (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        project_id TEXT NOT NULL UNIQUE,
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

    CREATE INDEX IF NOT EXISTS idx_leaderboard_cache_project_type ON leaderboard_cache(project_type);
    CREATE INDEX IF NOT EXISTS idx_leaderboard_cache_rank_overall ON leaderboard_cache(rank_overall);
    CREATE INDEX IF NOT EXISTS idx_leaderboard_cache_rank_in_category ON leaderboard_cache(rank_in_category);
    CREATE INDEX IF NOT EXISTS idx_leaderboard_cache_refreshed_at ON leaderboard_cache(refreshed_at DESC);
    """

    try:
        print("Creating verification_cache table...")
        client.client.rpc('exec_sql', {'query': create_verification_cache}).execute()

        print("Creating indexes for verification_cache...")
        client.client.rpc('exec_sql', {'query': create_indexes}).execute()

        print("Fixing leaderboard_cache table...")
        client.client.rpc('exec_sql', {'query': fix_leaderboard_cache}).execute()

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {e}")
        print("Trying alternative approach with individual queries...")

        # Try raw SQL execution
        queries = [
            create_verification_cache,
            create_indexes,
            fix_leaderboard_cache
        ]

        for i, query in enumerate(queries, 1):
            try:
                print(f"Executing query {i}...")
                result = client.client.postgrest.rpc('exec_sql', {'query': query}).execute()
                print(f"Query {i} succeeded")
            except Exception as e2:
                print(f"Query {i} failed: {e2}")

if __name__ == "__main__":
    apply_migration()