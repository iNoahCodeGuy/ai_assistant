# SYSTEM_ARCHITECTURE_SUMMARY.md
> *I’ll walk you through my blueprint like a staff engineer: clear responsibilities, explicit data contracts, and pragmatic tradeoffs. I’m serverless where possible and governed where it matters.*

## 1) Control flow (LangGraph nodes)
```
classify_intent
→ ensure_role_context
→ retrieve_context (pgvector top‑k)
→ generate_factual_answer (temp 0.2)
→ style_layer (narrative|data)
→ contextual_code_display? (technical users only)
→ generate_followup (temp 0.8, short)
→ log_event (messages, retrieval_logs, feedback)
```
- **Determinism first:** Factual answer is generated only after retrieval.
- **Mode switch:** Narrative (creative phrasing) vs Data (professional tables).
- **Optional code:** Shown when it clarifies backend/FE/pipeline mechanics.

## 2) RAG pipeline
1. **Embedding:** `text-embedding-3-small` encodes the user query.  
2. **Vector search:** `SELECT ... FROM kb_chunks ORDER BY embedding <=> $query LIMIT k` with IVFFLAT index.  
3. **Context assembly:** Merge top chunks + role instructions + link affordances (résumé, LinkedIn).  
4. **Generation:** `gpt-4o-mini` with bounded temperature and max tokens appropriate to role/intent.  
5. **Attribution:** Cite sections or KB labels where relevant (developer view).

## 3) Data layer (Supabase)
- **Tables:**
  - `messages(id, session_id, role_mode, user_query, assistant_answer, latency_ms, token_count, created_at, success)`
  - `retrieval_logs(id, message_id, chunk_id, similarity_score, grounded, created_at)`
  - `feedback(id, message_id, rating, comment(redacted), contact_requested, created_at)`
  - `kb_chunks(id, section, embedding, created_at)`
  - Optional: `confessions(id, is_anonymous, created_at)`, `sms_logs(...)`
- **RLS:** Enabled per table; server routes use service key only on the backend.
- **Storage:** Private bucket for résumé (signed URLs); public for headshot.

## 4) Frontend (Vercel)
- Single‑page chat with role selector.  
- Professional tables for analytics (fixed column sets, ISO timestamps, units).  
- Buttons for **Send Résumé**, **Open LinkedIn**, **Request Contact** (logs event + optional notifications).  
- Error states and loading spinners; retries on transient fetch errors.

## 5) Backend/API
- **/api/chat:** Role → retrieve → generate → log → respond.  
- **/api/analytics:** Returns inventory & last‑50 rows per table with PII redaction.  
- **/api/email:** Generates signed résumé URL and sends via Resend.  
- **/api/sms:** Twilio wrapper for alerts (resume sent, contact requested).  
- **/api/feedback:** Persists rating/comment; flags contact intent.

## 6) Reasoning about presentation (when to show what)
- **Show code** when: role is technical AND snippet clarifies a point (≤40 lines, inline comments, cite file path).  
- **Show tables/charts** when: user requests analytics, asks about performance, or asks “how is this measured?”.  
- **Long explanations** when: user asks “how/why” about architecture or enterprise scaling; otherwise summarize and offer drill‑down.  
- **Follow‑ups**: role‑aware, conversational, one‑liner options (pipeline diagram, SQL, code, or enterprise variant).

## 7) Enterprise adaptation path (overview)
- **Security:** Add SSO (SAML/OIDC), Secrets Manager, and per‑tenant RLS.  
- **Scale:** Move async work to queue (e.g., Neon logical replication + worker, or Vercel Queue/Cloud Tasks).  
- **Vector search:** Keep pgvector until scale demands dedicated vector service; preserve the retriever interface.  
- **Observability:** LangSmith traces + log‑based alerts; cost/latency dashboards.  
- **APIs:** Optionally front with API Gateway and WAF; add rate‑limits per role.

## 8) Tradeoffs & rationale
- **pgvector vs FAISS:** pgvector keeps retrieval **governed and SQL‑auditable**; FAISS is faster locally but adds devops overhead.  
- **Serverless vs long‑running:** Serverless is cheap and simple for a portfolio; queues/workers can be added when throughput grows.  
- **Single DB vs polyglot:** Start with Postgres for truth + vectors; add BigQuery/warehouse only if analytics scale demands.

**Ask me for the pipeline ASCII or for the `/api/analytics` contract — I’ll show you exactly how the parts fit and how I keep facts grounded.**
