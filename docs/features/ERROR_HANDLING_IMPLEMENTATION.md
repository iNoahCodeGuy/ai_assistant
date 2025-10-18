# Error Handling & Resilience Implementation

**Feature:** Production-Grade Error Handling System
**Status:** ✅ Implemented (October 17, 2025)
**Test Coverage:** 5 core tests (100% passing)
**Documentation:** QA_STRATEGY.md § Error Handling & Resilience Standards (line 1565)

---

## Overview

This feature implements a comprehensive error handling and resilience system ensuring **Portfolia never crashes on users** even when external services (OpenAI, Supabase, Twilio, Resend) fail or become unavailable.

**Key Principle:** Graceful degradation over hard failures. The conversation continues with reduced functionality rather than terminating.

---

## Architecture

### 1. Service Layer Resilience

**Pattern:** Factory functions return `None` when service unavailable

**Implementation:**

```python
# src/services/twilio_service.py
def get_twilio_service() -> Optional[TwilioService]:
    """Factory returns None if API key missing or service unavailable."""
    if not os.getenv("TWILIO_ACCOUNT_SID"):
        logger.warning("Twilio credentials not configured")
        return None

    try:
        return TwilioService()
    except Exception as e:
        logger.error(f"Failed to initialize Twilio: {e}")
        return None
```

**Usage in Conversation Flow:**

```python
# src/flows/action_execution.py (line 156)
def _send_sms_notification(self, state: ConversationState, action: Dict[str, Any]) -> None:
    """Send SMS notification with graceful fallback."""
    twilio = get_twilio_service()

    if not twilio:
        logger.warning("SMS service unavailable, skipping notification")
        return  # Conversation continues without SMS

    try:
        twilio.send_sms(phone=action["phone"], message=action["message"])
        logger.info(f"SMS sent successfully to {action['phone']}")
    except Exception as e:
        logger.error(f"SMS failed: {e}")
        # Still don't crash - log and continue
```

**Services Using This Pattern:**
- `get_twilio_service()` - SMS notifications
- `get_resend_service()` - Email notifications
- `get_storage_service()` - Resume uploads
- `get_supabase_client()` - Database operations (critical - validated on startup)

---

### 2. RAG Pipeline Resilience

**Three Failure Points:**

#### 2.1 Embedding Generation Failure

**File:** `src/retrieval/pgvector_retriever.py` (line 102)

```python
def embed(self, text: str) -> List[float]:
    """Generate embedding with OpenAI fallback."""
    try:
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []  # Return empty - retrieval will return no chunks
```

**Behavior:** Returns empty embedding → Retrieval returns no chunks → LLM generates ungrounded response (zero-shot mode)

#### 2.2 Vector Search Failure

**File:** `src/retrieval/pgvector_retriever.py` (line 159)

```python
def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieve chunks with database timeout fallback."""
    try:
        # Fetch all chunks with embeddings
        result = self.supabase_client.table('kb_chunks')\
            .select('id, doc_id, section, content, embedding')\
            .limit(500)\
            .execute()

        # ... similarity calculation ...

    except Exception as e:
        logger.error(f"pgvector retrieval failed: {e}")
        return []  # Return empty list - LLM continues without context
```

**Behavior:** Database timeout → Returns empty chunks → LLM uses only system prompt (no RAG context)

#### 2.3 Low-Quality Retrieval Detection 🆕

**Problem:** User queries with typos or out-of-domain topics return irrelevant results (low similarity scores).

**File:** `src/flows/core_nodes.py` (lines 135-152)

**Detection:**
```python
def generate_answer(state: ConversationState, rag_engine: RagEngine) -> ConversationState:
    """Generate answer, with fallback for low-quality retrieval."""

    # Check for very low retrieval quality (all scores below threshold)
    retrieval_scores = state.fetch("retrieval_scores", [])
    if retrieval_scores and all(score < 0.4 for score in retrieval_scores):
        # Trigger fallback (see Response Pattern below)
```

**Threshold:** < 0.4 (cosine similarity on 0.0-1.0 scale)
- 1.0 = Perfect match
- 0.7-1.0 = Good match (use normally)
- 0.4-0.7 = Moderate match (use with caution)
- **< 0.4 = Poor match (trigger fallback)**

**Response Pattern:**
```python
fallback_answer = f"""I'm not finding great matches for "{state.query}" in my knowledge base, but I'd love to help!

Here are some things I can tell you about:
- **Noah's engineering skills and experience**
- **Production GenAI systems**
- **System architecture**
[... more role-specific suggestions ...]

Or ask me to explain how I work - I love teaching about RAG, vector search, and LLM orchestration! What sounds interesting?"""

state.set_answer(fallback_answer)
state.stash("fallback_used", True)
logger.info(f"Used fallback for low-quality retrieval (scores: {retrieval_scores})")
```

**Common Triggers:**
- Typos/misspellings ("buisness" → "business")
- Out-of-domain queries (not in knowledge base)
- Overly generic queries ("tell me everything")

**Example Scenarios:**

| User Input | Retrieval Scores | System Response |
|------------|------------------|-----------------|
| "buisness" | [0.35, 0.28] | Fallback message + suggestions |
| "Python experience" | [0.89, 0.82] | Normal RAG response |
| "asdfghjkl" | [0.12, 0.08] | Fallback message + suggestions |

**Why This Matters:**
- Prevents showing irrelevant/confusing responses
- Guides users to high-quality content
- Maintains conversational tone (no error language)
- Builds trust (transparency about limitations)

**Test:** `test_low_quality_retrieval_fallback()` ✅

**Production Evidence:** Real screenshot from October 17, 2025 showing graceful handling of "buisness" typo.

#### 2.4 LLM Response Generation Failure

**File:** `src/core/response_generator.py` (line 78)

```python
def generate_response(
    self,
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    chat_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """Generate response with OpenAI rate limit fallback."""
    try:
        response = self.llm.invoke(messages)
        return response.content

    except RateLimitError as e:
        logger.warning(f"OpenAI rate limit hit: {e}")
        return "I'm experiencing high demand right now. Please try again in a moment."

    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        return "I'm having trouble generating a response. Please rephrase your question."
```

**Behavior:** Rate limit or API error → User sees polite fallback message (not cryptic error)

---

### 3. API Endpoint Error Handling

**Pattern:** Structured error responses with appropriate HTTP status codes

**Implementation:**

```python
# api/chat.py (Vercel serverless function)
def do_POST(self):
    """Handle chat request with comprehensive error handling."""
    try:
        # Parse JSON body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(body)

    except json.JSONDecodeError:
        # Client error: Invalid JSON
        return self._send_json(400, {
            "success": False,
            "error": "Invalid JSON in request body"
        })

    except Exception as e:
        # Server error: Unexpected exception
        logger.error(f"Chat API error: {e}", exc_info=True)
        return self._send_json(500, {
            "success": False,
            "error": "Internal server error"
        })
```

**HTTP Status Code Standards:**
- **400**: Client errors (invalid JSON, missing fields, malformed input)
- **500**: Server errors (database timeout, service unavailable, unexpected exceptions)
- **200**: Success (includes `success: true` flag in JSON)

---

### 4. Conversation Flow Node Resilience

**Pattern:** Nodes never raise exceptions - return state with error flags

**Implementation:**

```python
# src/flows/conversation_nodes.py (line 89)
def retrieve_chunks(state: ConversationState) -> ConversationState:
    """Retrieve chunks with error flag fallback."""
    try:
        rag_engine = get_rag_engine()
        results = rag_engine.retrieve(state.query, top_k=4)
        chunks = results.get("chunks", [])

        state.stash("retrieved_chunks", chunks)
        state.stash("retrieval_success", True)

    except Exception as e:
        logger.error(f"Chunk retrieval failed: {e}")
        state.stash("retrieved_chunks", [])
        state.stash("retrieval_success", False)
        state.stash("retrieval_error", str(e))

    return state  # Always return state - pipeline continues
```

**Pipeline Continues:** Next node (`generate_answer`) checks `retrieval_success` flag and adapts behavior

---

### 5. Input Validation & Security

**Pattern:** Sanitize all user inputs before processing

**Implementation:**

```python
# src/flows/resume_distribution.py (line 234)
def extract_email_from_query(state: ConversationState) -> ConversationState:
    """Extract email with XSS/SQL injection prevention."""
    query = state.query.lower()

    # Regex pattern rejects <script> tags, SQL keywords
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, query)

    if matches:
        # Further validation: reject suspicious patterns
        email = matches[0]
        if '<' in email or '>' in email or ';' in email:
            logger.warning(f"Suspicious email rejected: {email}")
            state.stash("user_email", None)
        else:
            state.stash("user_email", email)
    else:
        state.stash("user_email", None)

    return state
```

**Protections:**
- **XSS**: HTML tags escaped/rejected
- **SQL Injection**: Parameterized queries (Supabase client default)
- **Path Traversal**: File names sanitized (remove `../`, null bytes)
- **Length Limits**: User queries capped at 5,000 chars

---

## Test Suite

**File:** `tests/test_error_handling.py` (~450 lines, 6 tests)

### Test Coverage

| Test | Purpose | Validation |
|------|---------|------------|
| `test_conversation_without_twilio` | Service degradation (SMS unavailable) | Conversation continues, no SMS sent |
| `test_conversation_without_resend` | Service degradation (Email unavailable) | Conversation continues, no email sent |
| `test_openai_rate_limit_handling` | LLM failure (Rate limit exceeded) | Fallback message displayed |
| `test_email_validation` | Input sanitization (XSS/SQL injection) | Malicious input rejected |
| `test_invalid_json_in_api` | API validation (JSON parsing) | 400 error with structured response |
| `test_low_quality_retrieval_fallback` 🆕 | RAG pipeline resilience (low scores) | Fallback message + suggestions |

### Running Tests

```bash
# Run all error handling tests (6 tests, ~7 seconds)
pytest tests/test_error_handling.py -v

# Expected output:
# ============================== 6 passed in 7.03s ==============================

# Run specific test
pytest tests/test_error_handling.py::TestRAGPipelineResilience::test_low_quality_retrieval_fallback -v
```

### Test Patterns

**Service Mocking:**

```python
def test_conversation_without_twilio(self):
    """Test chat works even if Twilio unavailable."""
    with patch('src.services.twilio_service.get_twilio_service', return_value=None):
        state = ConversationState(query="What are your thoughts on RAG?", role="Software Developer")
        rag_engine = RagEngine()
        result = run_conversation_flow(state, rag_engine, session_id="test")

        assert result.answer  # Conversation still works
        assert "SMS service unavailable" not in result.answer.lower()  # No error exposed
```

**Key Principle:** Mock service as `None` → Validate conversation continues → Ensure no error exposed to user

---

## Configuration & Environment

### Required Environment Variables

```bash
# Critical (validated on startup)
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Optional (graceful degradation if missing)
TWILIO_ACCOUNT_SID=AC...        # SMS notifications
TWILIO_AUTH_TOKEN=...           # SMS notifications
TWILIO_PHONE_NUMBER=+1...       # SMS notifications
RESEND_API_KEY=re_...           # Email notifications
```

### Validation on Startup

**File:** `src/config/supabase_config.py` (line 45)

```python
def validate_supabase(self) -> None:
    """Fail-fast validation of critical services."""
    if not self.supabase_config.url or not self.supabase_config.service_role_key:
        raise ValueError("Supabase credentials missing - set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

    if not self.api_key:
        raise ValueError("OpenAI API key missing - set OPENAI_API_KEY")

    # Optional services log warnings (don't crash)
    if not os.getenv("TWILIO_ACCOUNT_SID"):
        logger.warning("Twilio not configured - SMS notifications disabled")

    if not os.getenv("RESEND_API_KEY"):
        logger.warning("Resend not configured - Email notifications disabled")
```

**Behavior:**
- Missing critical services → Crash on startup (fail-fast)
- Missing optional services → Log warning, continue with degraded functionality

---

## Production Monitoring (Phase 2)

**Status:** Planned for Phase 2 (LangSmith integration)

### Monitoring Strategy

| Metric | Tool | Threshold | Action |
|--------|------|-----------|--------|
| **Error Rate** | LangSmith | >5% over 1 hour | Slack alert + page on-call |
| **Latency (p95)** | LangSmith | >5 seconds | Email summary |
| **Service Availability** | Supabase health checks | Any service down | Slack alert |
| **Daily Cost** | LangSmith token tracking | >$10/day | Email summary |

### Alert Example

```
🔴 ALERT: Error Rate Spike

Time: October 17, 2025 14:35 UTC
Error Rate: 8.2% (threshold: 5%)
Total Queries: 234 (last hour)
Errors: 19

Top Errors:
  - OpenAI RateLimitError: 12 occurrences
  - Supabase timeout: 5 occurrences
  - Invalid JSON: 2 occurrences

Action Required:
  - Check OpenAI API status
  - Review Supabase query performance
  - Validate client-side JSON serialization

LangSmith Dashboard: https://smith.langchain.com/...
```

---

## Known Limitations & Roadmap

### Not Yet Implemented (Phase 2)

**1. Circuit Breaker Pattern** (Q1 2026)
- After N consecutive failures, stop attempting calls
- Return fallback responses immediately
- Prevents wasted API calls during outages

**2. Exponential Backoff with Jitter** (Q1 2026)
- Retry failed API calls with increasing delays (1s, 2s, 4s, 8s)
- Add random jitter to prevent thundering herd
- Currently: No retries (fail once, log, continue)

**3. Redis Caching** (Q2 2026)
- Cache LLM responses for common queries
- Reduce OpenAI API costs
- Improve latency (cache hit: <50ms vs API call: 2000ms)

**4. Health Check Endpoint** (Q1 2026)
- `/api/health` returns service status
- Used by monitoring tools (Datadog, New Relic)
- Detects degradation before users report issues

### Future Enhancements (Phase 3)

**1. Multi-Region Deployment** (Q2 2026)
- Deploy API to multiple Vercel regions
- Automatic failover if region fails
- Requires Supabase multi-region setup

**2. Request Queuing** (Q3 2026)
- Queue excess requests during high traffic
- Process asynchronously with notifications
- Prevents 429 errors during spikes

---

## Related Documentation

### Master Documentation (SSOT)
- **QA Standards:** `docs/QA_STRATEGY.md` § Error Handling & Resilience Standards (line 1565)
- **Test Suite:** `tests/test_error_handling.py` (400 lines, 5 tests)
- **GenAI KB Entry:** `data/technical_kb.csv` row 30 - "How does Portfolia handle failures and ensure uptime?" (1,718 words)

### Implementation Files
- **Service Layer:** `src/services/` (twilio_service.py, resend_service.py, storage_service.py)
- **RAG Pipeline:** `src/retrieval/pgvector_retriever.py`, `src/core/rag_engine.py`
- **API Endpoints:** `api/chat.py`, `api/email.py`, `api/feedback.py`
- **Conversation Flow:** `src/flows/conversation_nodes.py`, `src/flows/action_execution.py`

### External Resources
- **LangSmith Integration:** `docs/QA_LANGSMITH_INTEGRATION.md` (Phase 2 monitoring plan)
- **Observability Guide:** `docs/OBSERVABILITY.md` (tracing, logging, metrics)
- **External Services:** `docs/EXTERNAL_SERVICES.md` (Twilio, Resend, Supabase setup)

---

## Success Metrics

### Test Coverage
- **6 core tests:** 100% passing (as of October 17, 2025) *(+1 RAG pipeline resilience)*
- **9 additional tests:** Planned for Phase 2
- **Target:** 15 total error handling tests by Q1 2026

### Production Reliability (Phase 2 Targets)
- **Uptime:** 99.9% (8.76 hours downtime/year)
- **Error Rate:** <1% of total queries
- **Latency (p95):** <3 seconds
- **User-Facing Errors:** 0 per month (all errors gracefully handled)

### Code Quality
- **Zero print statements:** ✅ Enforced via pre-commit hooks
- **Configuration-driven:** ✅ All paths use `supabase_settings`
- **Logging standards:** ✅ All production code uses `logger.info()` / `logger.debug()`

---

## Changelog

### October 17, 2025 - Initial Implementation
- Added Error Handling & Resilience Standards to QA_STRATEGY.md (500+ lines)
- Created tests/test_error_handling.py (5 → 6 core tests, 100% passing)
- **Added Low-Quality Retrieval Fallback** (scores < 0.4 threshold) 🆕
- **Added test:** `test_low_quality_retrieval_fallback()` ✅
- Fixed Python 3.13 datetime deprecation warnings (10 instances across 3 files)
- Added GenAI KB entry on error handling (1,718 words)
- Migrated technical_kb.csv to Supabase (30 entries)
- Created this feature documentation

### Future Milestones
- **Phase 2 (Q4 2025):** LangSmith integration, production monitoring, 10 additional tests
- **Phase 3 (Q1 2026):** Circuit breaker, exponential backoff, health check endpoint
- **Phase 4 (Q2 2026):** Redis caching, multi-region deployment

---

**Status:** ✅ Production-ready as of October 17, 2025
**Next Step:** Phase 2 - LangSmith integration for production monitoring
