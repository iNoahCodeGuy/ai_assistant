#!/usr/bin/env python3
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from supabase import create_client
import os

openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

print('Testing OpenAI embedding with RPC...')
response = openai_client.embeddings.create(model='text-embedding-3-small', input='career background')
emb = response.data[0].embedding

print(f'Embedding: type={type(emb)}, length={len(emb)}, first_type={type(emb[0])}')

result = supabase.rpc('search_kb_chunks', {
    'query_embedding': emb,
    'match_threshold': 0.0,
    'match_count': 3
}).execute()

print(f'\n✅ Results: {len(result.data) if result.data else 0} rows')
if result.data:
    print('SUCCESS! The app should now work!')
    for i, r in enumerate(result.data[:2], 1):
        print(f'  [{i}] {r["content"][:80]}...')
else:
    print('❌ Still no results')
