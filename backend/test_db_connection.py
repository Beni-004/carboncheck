#!/usr/bin/env python3
"""Test database connection and schema"""

import os
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

print("=" * 60)
print("CARBONCHECK DATABASE CONNECTION TEST")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
print(f"   SUPABASE_URL: {os.getenv('SUPABASE_URL', 'NOT SET')}")
supabase_key = os.getenv('SUPABASE_SERVICE_KEY', 'NOT SET')
print(f"   SUPABASE_SERVICE_KEY: {'*' * 20}...{supabase_key[-10:] if supabase_key != 'NOT SET' else 'NOT SET'}")

# Test database connection
print("\n2. Database Connection:")
try:
    from app.db import db_client
    print("   ✓ Database client initialized")

    # Test health check
    if db_client.health_check():
        print("   ✓ Database health check passed")
    else:
        print("   ✗ Database health check failed")
except Exception as e:
    print(f"   ✗ Database connection failed: {e}")
    exit(1)

# Check if tables exist
print("\n3. Database Schema:")
tables_to_check = ["carbon_credits", "trust_scores", "leaderboard_cache"]

for table_name in tables_to_check:
    try:
        result = db_client.client.table(table_name).select("*").limit(1).execute()
        row_count = len(result.data) if hasattr(result, 'data') else 0
        print(f"   ✓ Table '{table_name}' exists ({row_count} rows in sample)")
    except Exception as e:
        print(f"   ✗ Table '{table_name}' error: {str(e)[:80]}")

# Get row counts
print("\n4. Data Summary:")
for table_name in tables_to_check:
    try:
        result = db_client.client.table(table_name).select("id", count="exact").execute()
        count = result.count if hasattr(result, 'count') else 0
        print(f"   {table_name}: {count} rows")
    except Exception as e:
        print(f"   {table_name}: Unable to count")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
