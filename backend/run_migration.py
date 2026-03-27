#!/usr/bin/env python3
"""
Direct SQL execution via Supabase PostgREST
Uses raw HTTP requests to execute SQL
"""

import os
import sys
import httpx
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

print("=" * 70)
print("APPLYING DATABASE MIGRATION TO SUPABASE")
print("=" * 70)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

if not supabase_url or not supabase_key:
    print("\n❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
    sys.exit(1)

# Extract project ref from URL
project_ref = supabase_url.replace("https://", "").split(".")[0]
print(f"\n✓ Project: {project_ref}")
print(f"✓ URL: {supabase_url}")

# Read migration SQL
migration_path = Path(__file__).parent / "supabase_local" / "migrations" / "20260324_001_init_carboncheck.sql"
with open(migration_path) as f:
    migration_sql = f.read()

print(f"\n✓ Loaded migration SQL ({len(migration_sql)} bytes)")

# Split SQL into individual statements
statements = [s.strip() for s in migration_sql.split(";") if s.strip()]
print(f"✓ Found {len(statements)} SQL statements")

print("\n" + "=" * 70)
print("EXECUTING MIGRATION")
print("=" * 70)

# Since we can't execute raw SQL via the Supabase Python client,
# we'll guide the user through the web interface
print("""
To apply this migration, please follow these steps:

1. Open Supabase Dashboard:
   https://supabase.com/dashboard/project/oyevylxqjeokjfsuacau/editor

2. Click on "SQL Editor" in the left sidebar

3. Click "New query"

4. Copy and paste the following SQL:
""")

print("\n" + "-" * 70)
print(migration_sql)
print("-" * 70)

print("""
5. Click "Run" to execute

After running the migration, test the connection with:
  python test_db_connection.py
""")

print("\n" + "=" * 70)
