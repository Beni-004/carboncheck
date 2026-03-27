#!/usr/bin/env python3
"""
Create database tables using Supabase Python client
Since we can't run raw SQL, we'll need to use the dashboard or psql
This script will help guide you through the process
"""

import os
import sys
import webbrowser
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

supabase_url = os.getenv("SUPABASE_URL")
project_ref = supabase_url.replace("https://", "").split(".")[0] if supabase_url else ""

print("\n" + "=" * 70)
print("CARBONCHECK - DATABASE MIGRATION SETUP")
print("=" * 70)

print(f"""
Your Supabase project: {project_ref}

STEP 1: Open Supabase SQL Editor
-----------------------------------
Opening your browser to:
https://supabase.com/dashboard/project/{project_ref}/sql/new

STEP 2: Copy the SQL below and paste it into the SQL Editor
------------------------------------------------------------
""")

# Read and print the migration SQL
migration_path = Path(__file__).parent / "supabase_local" / "migrations" / "20260324_001_init_carboncheck.sql"
with open(migration_path) as f:
    migration_sql = f.read()

print(migration_sql)

print("\n" + "=" * 70)
print("STEP 3: Click 'RUN' in the SQL Editor")
print("=" * 70)

# Try to open browser
try:
    url = f"https://supabase.com/dashboard/project/{project_ref}/sql/new"
    print(f"\nOpening browser to: {url}")
    webbrowser.open(url)
    print("✓ Browser opened")
except:
    print(f"\n⚠ Could not open browser automatically")
    print(f"Please manually visit: https://supabase.com/dashboard/project/{project_ref}/sql/new")

print("\n" + "=" * 70)
print("After running the SQL, verify with:")
print("  python test_db_connection.py")
print("=" * 70 + "\n")
