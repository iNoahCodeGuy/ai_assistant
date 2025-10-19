#!/usr/bin/env python3
"""Quick API key validation script."""
import os
from dotenv import load_dotenv

load_dotenv()

print('🔍 Testing API Keys...\n')
print('=' * 60)

# 1. OpenAI
print('\n1. OpenAI API Key:')
openai_key = os.getenv('OPENAI_API_KEY', '')
if openai_key.startswith('sk-proj-') or openai_key.startswith('sk-'):
    print(f'   ✅ Format valid: {openai_key[:25]}...')
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        models = client.models.list()
        print(f'   ✅ CONNECTION SUCCESSFUL - {len(models.data)} models available')
    except Exception as e:
        print(f'   ❌ Connection failed: {str(e)[:80]}')
else:
    print('   ❌ Invalid or missing')

# 2. Supabase
print('\n2. Supabase:')
supabase_url = os.getenv('SUPABASE_URL', '')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY', '')
if supabase_url and supabase_key:
    print(f'   URL: ✅ {supabase_url}')
    print(f'   Key: ✅ {supabase_key[:35]}...')
    try:
        from supabase import create_client
        supabase = create_client(supabase_url, supabase_key)
        result = supabase.table('kb_chunks').select('id').limit(1).execute()
        print(f'   ✅ CONNECTION SUCCESSFUL')
    except Exception as e:
        error_msg = str(e)
        if 'relation "kb_chunks" does not exist' in error_msg:
            print(f'   ⚠️  Connected but table "kb_chunks" not found (need to run migration)')
        else:
            print(f'   ❌ Error: {error_msg[:100]}')
else:
    print('   ❌ Missing URL or key')

# 3. Resend
print('\n3. Resend API Key:')
resend_key = os.getenv('RESEND_API_KEY', '')
if resend_key.startswith('re_'):
    print(f'   ✅ Format valid: {resend_key[:25]}...')
else:
    print('   ❌ Invalid or missing')

# 4. Twilio
print('\n4. Twilio:')
twilio_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
twilio_token = os.getenv('TWILIO_AUTH_TOKEN', '')
twilio_from = os.getenv('TWILIO_FROM', '')
if twilio_sid and twilio_token and twilio_from:
    print(f'   SID: ✅ {twilio_sid[:25]}...')
    print(f'   Token: ✅ {twilio_token[:20]}...')
    print(f'   From: ✅ {twilio_from}')
else:
    print('   ❌ Missing credentials')

print('\n' + '=' * 60)
print('✅ Validation complete!\n')
