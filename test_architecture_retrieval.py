"""Test architecture KB retrieval"""

from config.supabase_config import get_supabase_client
from openai import OpenAI
from config.supabase_config import supabase_settings

# Initialize
openai_client = OpenAI(api_key=supabase_settings.api_key)
supabase = get_supabase_client()

# Test query
query = "can you display or reference code?"

print(f"Testing query: {query}")
print("=" * 70)

# Generate embedding
print("\n1. Generating embedding...")
response = openai_client.embeddings.create(
    model='text-embedding-3-small',
    input=query
)
embedding = response.data[0].embedding
print(f"✅ Generated {len(embedding)}-dim embedding")

# Search with different thresholds
thresholds = [0.5, 0.6, 0.7]

for threshold in thresholds:
    print(f"\n2. Searching with threshold={threshold}...")
    
    results = supabase.rpc(
        'match_kb_chunks',
        {
            'query_embedding': embedding,
            'match_threshold': threshold,
            'match_count': 5
        }
    ).execute()
    
    print(f"\n📊 Found {len(results.data)} results:")
    for i, row in enumerate(results.data[:5], 1):
        print(f"\n  {i}. Doc: {row['doc_id']} | Similarity: {row['similarity']:.3f}")
        print(f"     Section: {row['section'][:60]}...")
        print(f"     Content preview: {row['content'][:100]}...")

print("\n" + "=" * 70)
print("✅ Test complete!")
