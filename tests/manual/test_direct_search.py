#!/usr/bin/env python3
"""
Alternative pgvector retrieval using direct table queries instead of RPC.
This bypasses the search_kb_chunks function if it's not working.
"""
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client
from openai import OpenAI
import os
import json

# Initialize clients
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    import math
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)

def search_with_direct_query(query_text, top_k=5, threshold=0.3):
    """Search using direct table query and manual similarity calculation"""

    # 1. Generate query embedding
    response = openai_client.embeddings.create(
        model='text-embedding-3-small',
        input=query_text
    )
    query_embedding = response.data[0].embedding

    # 2. Get all chunks from database
    result = supabase.table('kb_chunks').select('id, doc_id, section, content, embedding').execute()

    # 3. Calculate similarities manually
    chunks_with_similarity = []
    for chunk in result.data:
        if chunk.get('embedding'):
            # Parse embedding if it's a string
            chunk_emb = chunk['embedding']
            if isinstance(chunk_emb, str):
                chunk_emb = json.loads(chunk_emb)

            # Calculate similarity
            similarity = cosine_similarity(query_embedding, chunk_emb)

            if similarity > threshold:
                chunks_with_similarity.append({
                    'id': chunk['id'],
                    'doc_id': chunk.get('doc_id'),
                    'section': chunk.get('section'),
                    'content': chunk['content'],
                    'similarity': similarity
                })

    # 4. Sort by similarity and return top_k
    chunks_with_similarity.sort(key=lambda x: x['similarity'], reverse=True)
    return chunks_with_similarity[:top_k]

# Test it
print("Testing direct query retrieval...")
query = "What is Noah's professional background?"
results = search_with_direct_query(query, top_k=3, threshold=0.3)

print(f"\nQuery: {query}")
print(f"Results: {len(results)}\n")

for i, chunk in enumerate(results, 1):
    print(f"{i}. Similarity: {chunk['similarity']:.4f}")
    print(f"   Content: {chunk['content'][:100]}...")
    print()
