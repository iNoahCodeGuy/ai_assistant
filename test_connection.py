#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test script to verify Supabase connection and API keys.
Run this from the project root: python test_connection.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("🔍 TESTING API KEYS AND SUPABASE CONNECTION")
print("=" * 70)

# Check OpenAI API Key
print("\n1️⃣  Checking OpenAI API Key...")
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key and openai_key.startswith("sk-"):
    print(f"   ✅ OpenAI API Key found (starts with: {openai_key[:10]}...)")
else:
    print("   ❌ OpenAI API Key missing or invalid!")
    sys.exit(1)

# Check Supabase URL
print("\n2️⃣  Checking Supabase URL...")
supabase_url = os.getenv("SUPABASE_URL")
if supabase_url and "supabase.co" in supabase_url:
    print(f"   ✅ Supabase URL found: {supabase_url}")
else:
    print("   ❌ Supabase URL missing or invalid!")
    sys.exit(1)

# Check Supabase Service Role Key
print("\n3️⃣  Checking Supabase Service Role Key...")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if service_key and service_key.startswith("eyJ"):
    # Check if it's the service_role key (not anon)
    if "service_role" in service_key or "service-role" in service_key:
        print(f"   ✅ Service Role Key found (starts with: {service_key[:20]}...)")
    else:
        print("   ⚠️  Key found, but might be 'anon' key instead of 'service_role'")
else:
    print("   ❌ Service Role Key missing or invalid!")
    sys.exit(1)

# Test Supabase connection
print("\n4️⃣  Testing Supabase connection...")
try:
    from supabase import create_client, Client
    
    supabase: Client = create_client(supabase_url, service_key)
    print("   ✅ Supabase client created successfully")
    
    # Test a simple query (table might not exist yet)
    print("\n5️⃣  Testing database query...")
    try:
        result = supabase.table("kb_chunks").select("id").limit(1).execute()
        print(f"   ✅ Database query successful! (Found {len(result.data)} rows)")
    except Exception as table_error:
        if "kb_chunks" in str(table_error) or "PGRST205" in str(table_error):
            print(f"   ⚠️  Table 'kb_chunks' doesn't exist yet (this is OK for first run)")
            print(f"   💡 You'll need to run the database migration first")
        else:
            raise table_error
    
except ImportError as e:
    print(f"   ❌ Missing required package: {e}")
    print("   💡 Run: pip install supabase")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    print("\n   💡 Troubleshooting:")
    print("      - Verify your Supabase URL is correct")
    print("      - Verify you're using the service_role key (not anon key)")
    print("      - Check if the kb_chunks table exists in your database")
    sys.exit(1)

# Test OpenAI connection
print("\n6️⃣  Testing OpenAI API connection...")
try:
    from openai import OpenAI
    
    client = OpenAI(api_key=openai_key)
    
    # Test with a small embedding request
    response = client.embeddings.create(
        input="test",
        model="text-embedding-3-small"
    )
    
    embedding_dim = len(response.data[0].embedding)
    print(f"   ✅ OpenAI API working! (Embedding dimension: {embedding_dim})")
    
except ImportError as e:
    print(f"   ❌ Missing required package: {e}")
    print("   💡 Run: pip install openai")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ OpenAI API failed: {e}")
    print("\n   💡 Troubleshooting:")
    print("      - Verify your OpenAI API key is correct")
    print("      - Check if you have API credits available")
    sys.exit(1)

print("\n" + "=" * 70)
print("🎉 CONNECTION TESTS PASSED!")
print("=" * 70)
print("\n📋 Next Steps:")
print("   1. Set up database schema:")
print("      - Go to Supabase Dashboard → SQL Editor")
print("      - Run the migration: supabase/migrations/001_initial_schema.sql")
print("   2. Run data migration: python scripts/migrate_data_to_supabase.py")
print("   3. Start the app: streamlit run src/main.py")
print("=" * 70)
