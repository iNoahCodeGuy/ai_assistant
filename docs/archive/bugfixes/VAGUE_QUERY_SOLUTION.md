# Vague Query Handling - Complete Implementation

## Problem Statement
When users asked vague single-word queries like "engineering", Portfolia responded with:
> "I don't have enough information to answer that question about Noah."

This happened because:
1. **Sparse knowledge base** - Limited engineering-specific content
2. **Poor semantic matching** - Single words don't match well with sentence-based embeddings
3. **No fallback behavior** - System failed silently instead of helping user refine their question

## Three-Part Solution

### ✅ Solution 1: Enriched Knowledge Base

Added 6 comprehensive engineering Q&A entries to `data/career_kb.csv`:

1. **"What are Noah's software engineering skills?"** (350 words)
   - Python, LangChain, RAG pipelines, vector databases
   - Full-stack: Streamlit, Flask, Vercel serverless
   - Git/GitHub, CI/CD, observability (LangSmith)
   - API integration, cloud deployment patterns

2. **"What engineering principles does Noah follow?"** (310 words)
   - Modular architecture (<200 lines per file)
   - Observability and structured logging
   - Error handling and graceful degradation
   - Documentation and testing practices
   - User-centered, role-based design

3. **"How does Noah approach system architecture?"** (330 words)
   - Data layer (Supabase + pgvector)
   - Retrieval layer (RAG with semantic search)
   - Orchestration layer (LangGraph nodes)
   - Presentation layer (role-aware formatting)
   - External services (email, SMS, storage)
   - Observability integration

4. **"What does Noah understand about production GenAI systems?"** (400 words)
   - Grounding & accuracy (RAG to prevent hallucinations)
   - Cost management (token tracking, model selection)
   - Latency optimization (async, caching, indexing)
   - Observability (LangSmith tracing)
   - Reliability (retry logic, fallbacks)
   - Context management and evaluation
   - Governance and PII handling

5. **"What GenAI patterns has Noah implemented?"** (380 words)
   - RAG with pgvector semantic search
   - Multi-stage LangGraph pipelines
   - Role-based prompting
   - Few-shot learning and streaming responses
   - Conversation memory and hybrid retrieval
   - Query classification and action planning
   - Graceful degradation

6. **"How does Noah debug and troubleshoot applications?"** (350 words)
   - Structured logging at key checkpoints
   - Observability tools (LangSmith tracing)
   - Analytics queries for pattern analysis
   - Git bisect for regression detection
   - Unit tests and error handling
   - Print debugging and Vercel logs
   - User feedback analysis

**Total new content:** ~2,120 words covering production engineering practices

### ✅ Solution 2: Query Expansion

**File:** `src/flows/query_classification.py`

Added `VAGUE_QUERY_EXPANSIONS` dictionary mapping 18 common vague queries to expanded versions:

```python
VAGUE_QUERY_EXPANSIONS = {
    "engineering": "What are Noah's software engineering skills, principles, and experience with production systems?",
    "skills": "What technical skills does Noah have in software engineering and AI?",
    "ai": "What is Noah's experience with AI, machine learning, and GenAI systems?",
    "rag": "What is Noah's experience with Retrieval-Augmented Generation?",
    "python": "How strong is Noah's Python and what has he built with it?",
    # ... 13 more mappings
}
```

**Implementation:**
1. Added `_expand_vague_query()` function
   - Detects queries with ≤2 words (likely vague)
   - Looks up expansion in dictionary
   - Returns expanded query or original if no match

2. Updated `classify_query()` node
   - Calls expansion function first
   - Stashes `expanded_query` and `vague_query_expanded` flag
   - Logs expansion for debugging

3. Modified `retrieve_chunks()` in `core_nodes.py`
   - Uses `expanded_query` if available
   - Falls back to original query
   - Logs when expansion is used

**Example flow:**
```
User query: "engineering"
  ↓ expand
Expanded: "What are Noah's software engineering skills, principles, and experience with production systems?"
  ↓ embed
Semantic search retrieves relevant chunks about engineering practices
```

### ✅ Solution 3: Fallback Responses

**File:** `src/flows/core_nodes.py`

Enhanced `generate_answer()` with two fallback conditions:

#### Condition 1: Vague Query with No Matches
```python
if state.fetch("vague_query_expanded", False) and len(retrieved_chunks) == 0:
    fallback_answer = """I'd love to answer your question about "{original_query}"!

Could you be more specific? For example:
- If you're curious about my engineering skills, try: "What are your software engineering skills?"
- If you want to know about specific technologies, ask: "What's your experience with Python and AI?"
...

I'm here to help you understand Noah's capabilities and how generative AI applications like me work. What would you like to explore?"""
```

#### Condition 2: Low Quality Retrieval
```python
if retrieval_scores and all(score < 0.4 for score in retrieval_scores):
    fallback_answer = """I'm not finding great matches for "{query}" in my knowledge base, but I'd love to help!

Here are some things I can tell you about:
- Noah's engineering skills and experience
- Production GenAI systems
- System architecture
...

Or ask me to explain how I work - I love teaching about RAG, vector search, and LLM orchestration!"""
```

**Fallback characteristics:**
- ✅ Acknowledges user's question
- ✅ Provides helpful suggestions (not just "I don't know")
- ✅ Matches Portfolia's conversational personality
- ✅ Invites further exploration
- ✅ Explains what she can help with
- ✅ Maintains enthusiasm and teaching focus

## How It Works Together

### Before (Broken Flow):
```
User: "engineering"
  ↓
Retrieve with "engineering" (poor semantic match)
  ↓
No good chunks found
  ↓
LLM generates: "I don't have enough information"
  ❌ User frustrated
```

### After (Fixed Flow):
```
User: "engineering"
  ↓
Expand to: "What are Noah's software engineering skills, principles, and experience?"
  ↓
Retrieve with expanded query (better semantic match)
  ↓
Find 6 new engineering Q&As + existing technical content
  ↓
LLM generates comprehensive answer about engineering skills
  ✅ User gets helpful response

Alternative path if still no matches:
  ↓
Detect vague_query_expanded + no chunks
  ↓
Provide fallback with specific suggestions
  ✅ User knows how to refine question
```

## Implementation Details

### Query Expansion Logic
- **Trigger:** Queries with ≤2 words
- **Method:** Dictionary lookup (O(1) performance)
- **Fallback:** Original query if no expansion found
- **Logging:** Info-level log for debugging
- **State tracking:** `expanded_query` and `vague_query_expanded` flags

### Retrieval Strategy
- **Model:** OpenAI `text-embedding-3-small` (1536 dimensions)
- **Database:** Supabase pgvector with cosine similarity
- **Threshold:** 0.3 (low for better recall)
- **Top-k:** 4 chunks (configurable)
- **Query used:** Expanded version for semantic search

### Fallback Activation
- **Priority 1:** Vague query + zero chunks → Expansion failed, help user
- **Priority 2:** All scores < 0.4 → Low quality matches, suggest alternatives
- **Format:** Conversational, with bullet list of suggestions
- **Tone:** Helpful, enthusiastic, teaching-focused (matches CONVERSATION_PERSONALITY.md)

## Testing the Solution

### Test Case 1: "engineering"
**Expected behavior:**
1. Query expanded to engineering skills question
2. Retrieves new Q&A content
3. Generates comprehensive answer covering:
   - Python, LangChain, RAG, vector databases
   - Architecture patterns and observability
   - Production GenAI understanding
   - Debugging and testing practices

### Test Case 2: "skills"
**Expected behavior:**
1. Expanded to "What technical skills does Noah have?"
2. Retrieves skills Q&A + technical entries
3. Comprehensive skills overview

### Test Case 3: "xyz" (nonsense query)
**Expected behavior:**
1. No expansion (not in dictionary)
2. Poor retrieval results (scores < 0.4)
3. Fallback response with suggestions

### Test Case 4: "Tell me about Noah's experience with RAG"
**Expected behavior:**
1. No expansion (already specific, >2 words)
2. Normal retrieval flow
3. RAG-specific content returned

## Knowledge Base Migration

The new engineering content needs to be embedded and stored in Supabase:

```bash
# Run migration (requires Supabase access)
python scripts/migrate_data_to_supabase.py
```

This will:
1. Read all career_kb.csv entries (including 6 new ones)
2. Generate OpenAI embeddings (batch API)
3. Insert into `kb_chunks` table with pgvector
4. Log migration stats and costs

**Note:** Migration runs automatically on deployment via GitHub Actions or can be triggered manually via Supabase dashboard.

## Metrics to Monitor

After deployment, track:
1. **Query expansion rate:** % of queries expanded
2. **Fallback activation rate:** % hitting fallback logic
3. **Retrieval quality:** Average similarity scores
4. **User satisfaction:** Follow-up questions vs conversation end
5. **Common vague queries:** Identify new patterns to add to expansion dict

## Future Improvements

### Short-term:
1. **Add more vague query mappings** based on user patterns
2. **A/B test expansion strategies** (dictionary vs LLM-based)
3. **Improve similarity threshold** based on retrieval metrics

### Medium-term:
1. **Semantic caching** for common expanded queries
2. **User feedback loop** ("Was this helpful?" buttons)
3. **Multi-turn expansion** ("Did you mean...?" clarification)

### Long-term:
1. **Neural query rewriting** using fine-tuned model
2. **Hybrid retrieval** (keyword + semantic)
3. **Dynamic knowledge base updates** without redeployment

## Files Changed

| File | Changes | Lines Added |
|------|---------|-------------|
| `data/career_kb.csv` | +6 engineering Q&As | ~1,500 words |
| `src/flows/query_classification.py` | Query expansion logic | +68 lines |
| `src/flows/core_nodes.py` | Fallback responses | +52 lines |
| `scripts/migrate_data_to_supabase.py` | Import fix | 1 line |

## Commit History

1. **d942dcd** - Portfolia branding update (name + personality)
2. **128fd43** - Vague query handling (THIS COMMIT)
   - Solution 1: Enriched KB
   - Solution 2: Query expansion
   - Solution 3: Fallback responses

## Success Criteria

✅ **Problem solved when:**
1. "engineering" query returns comprehensive answer (not "I don't have enough information")
2. Other vague queries (skills, ai, rag, etc.) work correctly
3. Fallback provides helpful guidance for truly unknown queries
4. User can understand how to ask better questions
5. Portfolia maintains conversational, teaching-focused tone

## Production Deployment

**Status:** ✅ Deployed to main branch (commit 128fd43)

**Vercel deployment:** Auto-triggered, will be live in ~30-60 seconds

**Knowledge base:** Migration needs to run to populate Supabase with new engineering content

**Testing checklist:**
- [ ] Try "engineering" query - should get comprehensive answer
- [ ] Try "skills" query - should expand and retrieve
- [ ] Try "rag" query - should explain RAG implementation
- [ ] Try nonsense query - should get helpful fallback
- [ ] Check logs for expansion events
- [ ] Verify retrieval quality scores in Supabase analytics
