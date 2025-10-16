# Software Developer Query Classification Fix

**Date**: October 12, 2025
**Issue**: "How does this product work?" query returning "no information"
**Root Cause**: Query classification + missing knowledge bases in Supabase

---

## Problem Diagnosis

### 1. Query Classification Issue

The query "how does this product work?" was being classified as `"general"` instead of `"technical"` because the classification logic only looked for specific keywords:

**Previous logic** (line 32 in `conversation_nodes.py`):
```python
elif any(term in lowered for term in ["code", "technical", "stack", "architecture", "implementation", "retrieval"]):
    state.stash("query_type", "technical")
```

This missed queries like:
- "How does this product work?"
- "How did you build this?"
- "Explain how the system works"

### 2. Missing Knowledge Bases

The original migration script (`migrate_data_to_supabase.py`) **only migrated career_kb.csv**:
```python
def read_career_kb(self, csv_path: str) -> List[Dict[str, str]]:
    """Read career knowledge base from CSV."""
```

This meant:
- ❌ `technical_kb.csv` not in Supabase (RAG system details, error handling, etc.)
- ❌ `architecture_kb.csv` not in Supabase (system diagrams, code examples)
- ✅ `career_kb.csv` in Supabase (career history, achievements)

**Impact**: Software Developer role queries about "how the system works" had no technical context to retrieve!

---

## Solution

### 1. Enhanced Query Classification

**Updated logic** (commit 8bc2e30):
```python
# Detect "how does [product/system/chatbot] work" queries as technical
elif any(term in lowered for term in ["code", "technical", "stack", "architecture", "implementation", "retrieval"]) \
     or (("how does" in lowered or "how did" in lowered or "explain how" in lowered)
         and any(word in lowered for word in ["product", "system", "chatbot", "assistant", "rag", "pipeline", "work", "built"])):
    state.stash("query_type", "technical")
```

**Now detects**:
- ✅ "How does this product work?" → `technical`
- ✅ "How did you build this?" → `technical`
- ✅ "Explain how the system works" → `technical`
- ✅ "How does the RAG pipeline work?" → `technical`
- ✅ "Show me the architecture" → `technical` (already worked)

### 2. Complete KB Migration Script

**Created**: `scripts/migrate_all_kb_to_supabase.py`

**Features**:
- Migrates **all 3 knowledge bases**: career, technical, architecture
- Supports selective migration: `--kb technical_kb`
- Force re-import: `--force`
- Batch embedding generation (100 texts per API call)
- Progress tracking with cost estimates
- Handles different CSV formats gracefully

**Usage**:
```bash
# Migrate all KBs
python scripts/migrate_all_kb_to_supabase.py --force

# Migrate specific KB
python scripts/migrate_all_kb_to_supabase.py --kb architecture_kb

# Check before overwriting
python scripts/migrate_all_kb_to_supabase.py
```

**Migration Results** (Oct 12, 2025 12:33 PM):
```
📊 Migration Summary
============================================================
   KBs migrated: 3
   Total chunks: 278
   Total embeddings: 278
   Total cost: $0.0003
   Time elapsed: 11.3s
============================================================
```

**Breakdown**:
- `career_kb`: 20 chunks (career history, achievements, experience)
- `technical_kb`: 13 chunks (RAG system details, error handling, database architecture)
- `architecture_kb`: 245 chunks (system diagrams, code examples, LangGraph flow)

---

## Software Developer Role Flow

**Now when a Software Developer asks**: "How does this product work?"

### 1. Classification
```
classify_query() → query_type = "technical"
```

### 2. Action Planning
```python
elif state.role == "Software Developer":
    if query_type == "technical":
        add_action("include_code_snippets")
        add_action("provide_data_tables")
        add_action("explain_stack_currency")
```

### 3. Retrieval
```python
# Retrieve from pgvector with role-aware filtering
chunks = pgvector_retriever.retrieve_for_role(
    query="How does this product work?",
    role="Software Developer",
    top_k=5
)
# Prioritizes technical_kb and architecture_kb chunks
```

### 4. Response Generation
```python
# Generate technical response with:
- Architecture diagrams from architecture_kb
- RAG system details from technical_kb
- Code snippets via retrieve_with_code()
- Technical follow-up questions (💡 Dive Deeper)
- Third-person language enforcement
```

---

## Testing Checklist

✅ **Query Classification**
- [x] "How does this product work?" → technical
- [x] "How did you build this?" → technical
- [x] "Explain how the RAG system works" → technical

✅ **Knowledge Base Coverage**
- [x] career_kb migrated (20 chunks)
- [x] technical_kb migrated (13 chunks)
- [x] architecture_kb migrated (245 chunks)
- [x] Total: 278 chunks in Supabase

✅ **Software Developer Role**
- [ ] Returns architecture diagrams when asked
- [ ] Includes code snippets for technical queries
- [ ] Suggests follow-up questions (💡 Dive Deeper)
- [ ] Uses third-person language ("Noah built...", not "I built...")

---

## Next Steps

1. **Deploy to Vercel** (commit 8bc2e30)
   - Query classification improvements
   - Vercel should auto-deploy from main branch push

2. **Test with user queries**:
   ```
   Role: Software Developer
   Query: "How does this product work?"

   Expected:
   - Returns RAG pipeline details
   - Shows architecture diagram (mermaid)
   - Includes code snippet from architecture_kb
   - Suggests follow-up: "💡 Dive Deeper: How does the pgvector retrieval optimize for technical queries?"
   ```

3. **Verify third-person language**:
   - "Noah built this system using..." ✅
   - NOT "I built this system using..." ❌

4. **Check code display preservation**:
   - Mermaid diagrams render properly
   - Python code blocks show syntax highlighting
   - No summarization of code (displays EXACT content)

---

## Related Files

**Modified**:
- `src/flows/conversation_nodes.py` (line 32) - Enhanced query classification

**Created**:
- `scripts/migrate_all_kb_to_supabase.py` - Complete KB migration script

**Knowledge Bases** (all now in Supabase):
- `data/career_kb.csv` (20 Q&A pairs)
- `data/technical_kb.csv` (13 Q&A pairs)
- `data/architecture_kb.csv` (245 entries with diagrams/code)

**Deployment**:
- Commit: 8bc2e30
- Branch: main
- Vercel: Auto-deploying now

---

## Cost & Performance

**Migration Cost**: $0.0003 USD (278 embeddings × $0.00002/1K tokens)

**Query Performance** (expected):
- Embedding generation: ~200ms
- pgvector search: ~50ms
- LLM generation: ~1-2s
- **Total**: ~2-3s per query

**Storage**:
- 278 chunks × 1536 dimensions = 426,528 floats
- ~1.7 MB embedding storage in Supabase

---

## Lessons Learned

1. **Query classification must be comprehensive**: Don't just match exact keywords, detect patterns like "how does [X] work"

2. **Migration scripts should be complete**: Original script only handled one KB, leaving technical/architecture content missing

3. **Role-specific retrieval matters**: Software Developer queries should prioritize technical_kb and architecture_kb over career_kb

4. **Test with real user queries**: "How does this product work?" is more natural than "Show me the architecture" but harder to classify

5. **Document migration state**: Clear logs showing what's in Supabase prevents debugging confusion
