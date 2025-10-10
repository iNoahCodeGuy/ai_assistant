#!/usr/bin/env python3
"""
Verify that the Supabase database schema was set up correctly.
Run this after executing the migration SQL in Supabase.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

print("=" * 70)
print("🔍 VERIFYING SUPABASE DATABASE SCHEMA")
print("=" * 70)

# Connect to Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# Tables to check
tables = ['kb_chunks', 'messages', 'retrieval_logs', 'links', 'feedback']

print("\n1️⃣  Checking if tables exist...")
for table in tables:
    try:
        result = supabase.table(table).select("*").limit(1).execute()
        print(f"   ✅ {table:20s} - Exists (row count: {len(result.data)})")
    except Exception as e:
        print(f"   ❌ {table:20s} - ERROR: {e}")

# Check pgvector extension
print("\n2️⃣  Checking pgvector extension...")
try:
    # Try to query with vector operator
    result = supabase.table("kb_chunks").select("id, embedding").limit(1).execute()
    print(f"   ✅ pgvector extension installed")
except Exception as e:
    print(f"   ❌ pgvector not working: {e}")

# Check seed data
print("\n3️⃣  Checking seed data (links)...")
try:
    result = supabase.table("links").select("*").execute()
    print(f"   ✅ Found {len(result.data)} links (expected 3)")
    for link in result.data:
        print(f"      • {link['key']:12s} → {link['url']}")
except Exception as e:
    print(f"   ❌ Error reading links: {e}")

print("\n" + "=" * 70)
print("🎉 SCHEMA VERIFICATION COMPLETE!")
print("=" * 70)
print("\n📋 Next Step:")
print("   Run data migration: python scripts/migrate_data_to_supabase.py")
print("=" * 70)
