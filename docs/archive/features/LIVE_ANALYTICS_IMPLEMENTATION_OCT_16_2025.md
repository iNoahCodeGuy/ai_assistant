# Live Analytics Display Implementation

**Status:** ✅ Implemented
**Branch:** main
**Policy:** DISPLAY_ANALYTICS_POLICY.md (v1.0)

---

## Overview

Implemented a live analytics dashboard system that fetches real-time data from Supabase and renders it in analyst-quality markdown tables with smart follow-up suggestions.

### Key Components

1. **API Endpoint** (`api/analytics.py`)
   - GET /api/analytics
   - Server-side only (uses service role key)
   - Rate limited: 6 requests/minute per IP
   - Returns JSON with all datasets + inventory

2. **SQL Helpers** (`supabase/migrations/003_analytics_helpers.sql`)
   - `kb_coverage_summary()` - Groups chunks by section
   - `low_similarity_queries()` - Identifies poor retrieval
   - `conversion_by_role()` - Analyzes contact requests
   - `performance_summary_7d()` - 7-day aggregate metrics
   - `tool_invocation_stats()` - Tool usage analytics

3. **Rendering Module** (`src/flows/analytics_renderer.py`)
   - `render_analytics_response()` - Formats tables
   - `analytics_cta()` - Smart follow-up suggestions
   - `redact_pii()` - Masks emails/phones in feedback

4. **Conversation Integration** (`src/flows/conversation_nodes.py`)
   - Updated `generate_answer()` to detect data display requests
   - Modified `plan_actions()` to use `render_live_analytics`
   - Enhanced `apply_role_context()` to fetch from /api/analytics

---

## Data Contracts

### API Response Schema

```json
{
  "inventory": {
    "messages": 1234,
    "retrieval_logs": 5678,
    "feedback": 42,
    "confessions": 7,
    "kb_chunks": 19,
    "sms_logs": 12
  },
  "messages": {
    "data": [
      {
        "id": "uuid",
        "role_mode": "Software Developer",
        "user_query": "How does RAG work?",
        "latency_ms": 1234,
        "token_count": 450,
        "created_at": "2025-01-30T12:00:00Z",
        "success": true
      }
    ]
  },
  "retrieval_logs": {
    "data": [
      {
        "message_id": "uuid",
        "chunk_id": "uuid",
        "similarity_score": 0.87,
        "grounded": true,
        "created_at": "2025-01-30T12:00:00Z"
      }
    ]
  },
  "feedback": {
    "data": [
      {
        "message_id": "uuid",
        "rating": 5,
        "comment": "[redacted]",  // PII masked
        "contact_requested": true,
        "created_at": "2025-01-30T12:00:00Z"
      }
    ]
  },
  "confessions": {
    "data": [
      {
        "id": "uuid",
        "is_anonymous": true,
        "created_at": "2025-01-30T12:00:00Z"
        // Note: message, name, contact NEVER included
      }
    ]
  },
  "kb_chunks": {
    "data": [
      {
        "id": "uuid",
        "section": "career",
        "created_at": "2025-01-30T12:00:00Z"
      }
    ]
  },
  "kb_coverage": [
    {"source": "career", "count": 12},
    {"source": "technical", "count": 7}
  ],
  "generated_at": "2025-01-30T12:00:00Z"
}
```

---

## Trigger Phrases (Case-Insensitive)

- `display data analytics`
- `show analytics`
- `show dashboard`
- `display metrics`
- `show data tables`
- `display logs`
- `display data`
- `show data`
- `collected data`
- `display collected data`
- `can you display`

---

## Role-Based Behavior

### Technical Roles (Hiring Manager - Technical, Software Developer)
- **Full access** to all datasets
- Shows all 7 tables including confessions (privacy-protected)
- Advanced follow-up options (low-similarity spotlight, tool invocations)

### Non-Technical Roles (Hiring Manager - Nontechnical, Just looking around)
- **Reduced view** without raw logs
- Simplified tables (inventory, messages summary, feedback only)
- Asks if they want technical detail

### Privacy Role (Looking to confess crush)
- **No analytics access** (confessions are private)

---

## Security & Privacy

### PII Redaction
```python
def redact_pii(text):
    # Emails: user@example.com → [redacted]
    # Phones: +1-555-1234 → [redacted]
    return text with PII masked
```

Applied to:
- `feedback.comment` field
- Any user-generated content

### Confessions Privacy
**NEVER display:**
- `confessions.message`
- `confessions.name`
- `confessions.contact`

**Only show:**
- `confessions.id`
- `confessions.is_anonymous`
- `confessions.created_at`

### Rate Limiting
- **6 requests/minute per IP**
- Returns 429 if exceeded
- In-memory store (use Redis for production scale)

### Authorization
- API route runs **server-side only**
- Uses Supabase service role key
- Never exposes credentials to client

---

## Performance

### Timeouts
- **Per-query timeout:** 2.5 seconds
- **Total route budget:** 1.2-1.8 seconds
- Returns `{ data:[], error:"timeout" }` if exceeded

### Pagination
- **Max 50 rows** per table
- Ordered by `created_at desc`
- Inventory uses `head:true, count:"exact"`

### Payload Size
- **Target:** < 200KB total
- Truncates long text to 140 chars
- Sample only 20 KB chunks

---

## Error Handling

### Partial Failures
If one table fails:
```markdown
## Messages
*Could not load due to timeout; try again.*
```

Other tables still render normally.

### Total Failure
If all tables fail:
```
Analytics temporarily unavailable; would you like a cached summary instead?
```

### Empty States
```markdown
## Messages (Last 50)
No messages records found.
```

---

## Follow-Up Actions

After displaying analytics, the system offers:

```markdown
💡 **Would you like me to:**
- Explain the importance of **{detected focus}**
- Display the **data pipeline** architecture
- Show **other datasets** (tool invocations, cost by role, low-similarity queries)
- Generate a **7-day performance report** with aggregated metrics
```

**Detected focus heuristic:**
- Defaults to "a dataset above"
- Can be enhanced to detect last scrolled table
- Future: track user click events

---

## SQL Helpers Usage

### Check KB coverage
```sql
select * from kb_coverage_summary();
```

### Find low-similarity queries
```sql
select * from low_similarity_queries(7, 20);  -- last 7 days, top 20
```

### Analyze conversions
```sql
select * from conversion_by_role(30);  -- last 30 days
```

### Get performance metrics
```sql
select * from performance_summary_7d();
```

### Tool invocation stats
```sql
select * from tool_invocation_stats(7);  -- last 7 days
```

---

## Testing

### Contract Test
```python
import requests
response = requests.get("https://noahsaiassistant.vercel.app/api/analytics")
assert response.status_code == 200
data = response.json()
assert "inventory" in data
assert "messages" in data
assert "generated_at" in data
```

### PII Redaction Test
```python
from api.analytics import redact_pii
assert redact_pii("Contact me at user@example.com") == "Contact me at [redacted]"
assert redact_pii("Call +1-555-1234") == "Call [redacted]"
```

### Rate Limit Test
```python
for i in range(7):
    response = requests.get(url)
    if i < 6:
        assert response.status_code == 200
    else:
        assert response.status_code == 429
```

---

## Deployment Checklist

- [x] Create `/api/analytics.py` endpoint
- [x] Add SQL helpers to `003_analytics_helpers.sql`
- [x] Implement PII redaction
- [x] Create `analytics_renderer.py` module
- [x] Update `conversation_nodes.py` integration
- [x] Add `requests` to `requirements.txt`
- [ ] Run SQL migration in Supabase dashboard
- [ ] Test live endpoint in production
- [ ] Verify PII masking
- [ ] Confirm rate limiting works
- [ ] Test all role types

---

## Migration Steps

### 1. Apply SQL Helpers
```bash
# Go to Supabase Dashboard → SQL Editor → New Query
# Copy/paste content from: supabase/migrations/003_analytics_helpers.sql
# Click "Run"
```

### 2. Deploy to Vercel
```bash
git add -A
git commit -m "feat: Implement live analytics dashboard per DISPLAY_ANALYTICS_POLICY"
git push origin main
# Vercel auto-deploys
```

### 3. Test Endpoint
```bash
curl https://noahsaiassistant.vercel.app/api/analytics
```

### 4. Test in Chat
```
User: "display data analytics"
Assistant: [Renders live dashboard with all tables]
```

---

## Complexity Analysis (Louridas Framing)

- **Finiteness:** Bounded pagination (max 50 rows), timeouts (2.5s)
- **Definiteness:** Exact table order, columns, CTA format specified
- **Effectiveness:** Simple SELECT queries, O(n) processing
- **Time complexity:** O(n) where n ≤ 50 per table
- **Space complexity:** O(n) for response payload, O(1) code memory

---

## Ownership

- **Code owner:** @noah
- **Tables owner:** @noah (Supabase)
- **SLO:** ≥ 99.5% success rate, p95 latency ≤ 2.5s
- **Monitoring:** Alert if 5xx rate > 5% over 15 minutes

---

## Version History

- **v1.0 (2025-01-30):** Initial implementation
  - API endpoint with rate limiting
  - 5 SQL helper functions
  - PII redaction
  - Role-based rendering
  - Smart follow-up CTAs

---

## Future Enhancements

1. **Redis rate limiting** (replace in-memory store)
2. **WebSocket streaming** for real-time updates
3. **CSV/Excel export** option
4. **Custom date ranges** for queries
5. **Interactive charts** (Plotly/Chart.js)
6. **Focus detection** based on user scroll/clicks
7. **Caching layer** (5-minute TTL for inventory)
8. **MCP integration** (`mcp.call("analytics_read")`)

---

## References

- Policy: `DISPLAY_ANALYTICS_POLICY.md`
- Endpoint: `/api/analytics.py`
- SQL: `supabase/migrations/003_analytics_helpers.sql`
- Renderer: `src/flows/analytics_renderer.py`
- Integration: `src/flows/conversation_nodes.py`
