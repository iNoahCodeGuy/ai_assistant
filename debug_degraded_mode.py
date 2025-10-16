"""
Debug script for [DEGRADED MODE SYNTHESIS] bug
Tests OpenAI API, career_kb retrieval, and response generation
"""

import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, 'src')

load_dotenv()

print("=" * 70)
print("🔍 DEBUGGING [DEGRADED MODE SYNTHESIS] BUG")
print("=" * 70)

# Test 1: OpenAI API Connection
print("\n📡 Test 1: OpenAI API Connection")
print("-" * 70)

try:
    from openai import OpenAI
    from config.supabase_config import supabase_settings

    client = OpenAI(api_key=supabase_settings.api_key)

    # Test embedding
    print("Testing embedding generation...")
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="test query"
    )
    print(f"✅ Embedding API works! Dimension: {len(response.data[0].embedding)}")

    # Test chat completion
    print("\nTesting chat completion...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'API working' if you can respond."}
        ],
        max_tokens=50
    )
    answer = response.choices[0].message.content
    print(f"✅ Chat API works! Response: {answer}")

except Exception as e:
    print(f"❌ OpenAI API FAILED: {e}")
    print("\nPossible causes:")
    print("  - Invalid API key")
    print("  - Network connection issue")
    print("  - Rate limit exceeded")
    sys.exit(1)

# Test 2: Career KB Retrieval
print("\n" + "=" * 70)
print("📚 Test 2: Career KB Retrieval")
print("-" * 70)

try:
    from config.supabase_config import get_supabase_client

    supabase = get_supabase_client()

    # Check if career_kb chunks exist
    result = supabase.table('kb_chunks').select('*').eq('doc_id', 'career_kb').execute()

    if not result.data:
        print("❌ NO CAREER_KB CHUNKS FOUND IN DATABASE!")
        print("\nThis is the root cause! The database has no career information.")
        print("\nFix: Run migration script:")
        print("  python scripts/migrate_data_to_supabase.py")
        sys.exit(1)

    print(f"✅ Found {len(result.data)} career_kb chunks")
    print("\nSample chunks:")
    for i, chunk in enumerate(result.data[:3], 1):
        print(f"  {i}. {chunk['section'][:60]}...")

    # Test retrieval with actual query
    print("\nTesting vector search with career query...")

    # Generate embedding for test query
    test_query = "what is noah's professional background?"
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=test_query
    ).data[0].embedding

    # Search using RPC function
    search_result = supabase.rpc(
        'search_kb_chunks',
        {
            'query_embedding': embedding,
            'match_threshold': 0.5,  # Lower threshold for testing
            'match_count': 3
        }
    ).execute()

    if not search_result.data:
        print("❌ NO CHUNKS RETRIEVED! Similarity scores too low.")
        print("\nPossible causes:")
        print("  - Career KB doesn't have professional background info")
        print("  - Embedding mismatch")
        print("  - Threshold too high")
    else:
        print(f"✅ Retrieved {len(search_result.data)} chunks")
        for i, chunk in enumerate(search_result.data, 1):
            print(f"  {i}. Similarity: {chunk.get('similarity', 'N/A'):.3f} - {chunk['section'][:50]}...")

except Exception as e:
    print(f"❌ Career KB retrieval FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Response Generation
print("\n" + "=" * 70)
print("🤖 Test 3: Response Generation")
print("-" * 70)

try:
    from core.rag_engine import RagEngine
    from agents.role_router import RoleRouter
    from core.memory import Memory

    # Initialize components
    rag_engine = RagEngine()
    role_router = RoleRouter()
    memory = Memory()

    # Test query
    query = "what is noah's professional background?"
    role = "Hiring Manager (nontechnical)"  # Match exact role name

    print(f"Query: {query}")
    print(f"Role: {role}")
    print("\nProcessing...")

    # Get response through role router
    result = role_router.route(role, query, memory, rag_engine)

    print("\n📋 Response Preview:")
    print("-" * 70)
    response = result.get('response', '')

    # Check for degraded mode indicators
    if '[DEGRADED MODE SYNTHESIS]' in response or 'User question:' in response:
        print("❌ DEGRADED MODE DETECTED!")
        print("\nRaw response:")
        print(response[:500])
        print("\nThis is the bug! System prompt is leaking into response.")
    elif 'see Noah\'s LinkedIn' in response and 'User question:' in response:
        print("❌ PROMPT TEMPLATE LEAK DETECTED!")
        print("\nThe response contains the raw prompt instead of LLM output.")
    else:
        print("✅ Response looks good!")
        print(response[:300] + "...")

    # Check context
    if result.get('context'):
        print(f"\n✅ Context included: {len(result['context'])} chunks")
    else:
        print("\n⚠️  No context in response")

except Exception as e:
    print(f"❌ Response generation FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check Response Generator Directly
print("\n" + "=" * 70)
print("🔬 Test 4: Direct Response Generator Test")
print("-" * 70)

try:
    from core.response_generator import ResponseGenerator

    generator = ResponseGenerator()

    # Simulate retrieved context
    mock_context = [
        {
            'content': 'Noah is a software engineer with experience in AI/ML.',
            'similarity': 0.85,
            'doc_id': 'career_kb',
            'section': 'Professional Background'
        }
    ]

    test_query = "What is Noah's background?"

    print("Testing direct LLM call...")
    response = generator.generate_response(
        query=test_query,
        context=mock_context,
        role="Hiring Manager"
    )

    if isinstance(response, str):
        if '[DEGRADED MODE' in response or 'User question:' in response:
            print("❌ DEGRADED MODE in direct generator call!")
            print("\nThis means the bug is in response_generator.py")
            print("\nRaw output:")
            print(response[:400])
        else:
            print("✅ Direct generator works!")
            print(f"\nResponse: {response[:200]}...")
    else:
        print(f"⚠️  Unexpected response type: {type(response)}")
        print(response)

except Exception as e:
    print(f"❌ Direct generator test FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("🏁 DEBUGGING COMPLETE")
print("=" * 70)
print("\n📋 Summary:")
print("  1. Check OpenAI API - see results above")
print("  2. Check career_kb retrieval - see results above")
print("  3. Check response generation - see results above")
print("  4. Check direct generator - see results above")
print("\n💡 Next steps:")
print("  - Fix identified issues")
print("  - Add error handling")
print("  - Test in actual app")
