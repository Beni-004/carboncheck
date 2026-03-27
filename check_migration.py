#!/usr/bin/env python3
"""
Simple migration script.
"""

import os
import sys
sys.path.append('/home/iyad/Projects/carboncheck/backend')

from app.db import get_db_client

def check_and_create_tables():
    """Check if tables exist and create them if they don't."""
    client = get_db_client()

    try:
        # Test if verification_cache exists by trying to query it
        print("Checking if verification_cache exists...")
        result = client.client.table("verification_cache").select("count").limit(1).execute()
        print("verification_cache table exists")
    except Exception as e:
        if "table" in str(e).lower() and "not" in str(e).lower():
            print("verification_cache table does not exist, but we can't create it via Supabase client")
            print("Please run the SQL migration manually in your Supabase dashboard")
        else:
            print(f"Error checking verification_cache: {e}")

    try:
        # Test leaderboard insert to see if UNIQUE constraint exists
        print("Testing leaderboard_cache UNIQUE constraint...")
        test_data = {
            "project_id": "TEST-123",
            "project_type": "forestry",
            "total_score": 50.0,
            "verdict": "WARNING",
            "registry_name": "test",
            "claimed_tco2": 1000.0,
            "rank_overall": 1,
            "rank_in_category": 1
        }

        # Try to insert the same data twice
        client.client.table("leaderboard_cache").insert(test_data).execute()
        client.client.table("leaderboard_cache").insert(test_data).execute()
        print("WARNING: UNIQUE constraint is NOT working - inserted duplicate data")

        # Clean up
        client.client.table("leaderboard_cache").delete().eq("project_id", "TEST-123").execute()

    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            print("UNIQUE constraint is working correctly")
        else:
            print(f"Error testing leaderboard_cache: {e}")

if __name__ == "__main__":
    check_and_create_tables()