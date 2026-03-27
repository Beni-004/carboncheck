#!/usr/bin/env python3
"""
Apply database migration to Supabase
Runs the SQL migration file against the Supabase database
"""

import os
import sys
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
print("CARBONCHECK DATABASE MIGRATION")
print("=" * 70)

# Read the migration SQL
migration_path = Path(__file__).parent / "supabase_local" / "migrations" / "20260324_001_init_carboncheck.sql"
if not migration_path.exists():
    print(f"\n❌ Migration file not found: {migration_path}")
    sys.exit(1)

with open(migration_path) as f:
    migration_sql = f.read()

print(f"\n✓ Loaded migration: {migration_path.name}")
print(f"  SQL size: {len(migration_sql)} bytes")

# Connect to Supabase
try:
    from supabase import create_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        print("\n❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
        sys.exit(1)

    print(f"\n✓ Connecting to: {supabase_url}")
    client = create_client(supabase_url, supabase_key)

except Exception as e:
    print(f"\n❌ Failed to initialize Supabase client: {e}")
    sys.exit(1)

# Execute migration using Supabase REST API
# Note: Supabase Python client doesn't have direct SQL execution
# We need to use psql or the Supabase dashboard SQL editor
print("\n" + "=" * 70)
print("MIGRATION INSTRUCTIONS")
print("=" * 70)
print("""
The Supabase Python client doesn't support raw SQL execution.
You have 3 options to run the migration:

OPTION 1 - Supabase Dashboard (Recommended):
1. Go to: https://oyevylxqjeokjfsuacau.supabase.co
2. Navigate to SQL Editor
3. Copy the contents from: backend/supabase_local/migrations/20260324_001_init_carboncheck.sql
4. Paste and run the SQL

OPTION 2 - Using psql:
If you have PostgreSQL client installed:
  psql "postgresql://postgres.[project-ref]:[password]@aws-0-us-east-1.pooler.supabase.com:6543/postgres" -f backend/supabase_local/migrations/20260324_001_init_carboncheck.sql

OPTION 3 - Install Supabase CLI:
  npm install -g supabase
  supabase link --project-ref oyevylxqjeokjfsuacau
  supabase db push
""")

# Print the SQL for easy copy-paste
print("\n" + "=" * 70)
print("SQL TO RUN (copy everything below):")
print("=" * 70)
print(migration_sql)
print("=" * 70)
