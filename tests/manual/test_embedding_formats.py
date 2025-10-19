#!/usr/bin/env python3
"""Test if PostgREST needs the embedding as a JSON string"""
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from supabase import create_client
import os
import json

openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

print('Testing different embedding formats...')
response = openai_client.embeddings.create(model='text-embedding-3-small', input='career')
emb_list = response.data[0].embedding

# Try 1: As list
print('\n[1] Testing as list...')
result1 = supabase.rpc('search_kb_chunks', {
    'query_embedding': emb_list,
    'match_threshold': 0.0,
    'match_count': 3
}).execute()
print(f'    Results: {len(result1.data) if result1.data else 0}')

# Try 2: As JSON string
print('\n[2] Testing as JSON string...')
emb_json = json.dumps(emb_list)
result2 = supabase.rpc('search_kb_chunks', {
    'query_embedding': emb_json,
    'match_threshold': 0.0,
    'match_count': 3
}).execute()
print(f'    Results: {len(result2.data) if result2.data else 0}')

# Try 3: As array string
print('\n[3] Testing as PostgreSQL array string...')
emb_array = '[' + ','.join(str(x) for x in emb_list) + ']'
result3 = supabase.rpc('search_kb_chunks', {
    'query_embedding': emb_array,
    'match_threshold': 0.0,
    'match_count': 3
}).execute()
print(f'    Results: {len(result3.data) if result3.data else 0}')

print('\n' + '='*60)
if any(result.data for result in [result1, result2, result3]):
    print('✅ One of the formats worked!')
else:
    print('❌ None of the formats worked - PostgREST may need restart')
