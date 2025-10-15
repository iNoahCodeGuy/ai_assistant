# 🤖 Copilot Context — Noah’s AI Assistant (Full-Stack + LangGraph System)

## 🎯 Product Overview
Noah’s AI Assistant is a **full-stack Retrieval-Augmented Generation (RAG)** application serving as an **interactive résumé and AI portfolio assistant**. 
It’s built to demonstrate **senior-level AI system design** with code clarity that’s easy for a **junior developer** to understand.

The project showcases:
- Role-based reasoning with **LangGraph orchestration**
- **RAG pipeline** using pgvector (Supabase)
- Automated **data collection and observability**
- **Actionable responses** (email résumé, LinkedIn, SMS notifications)
- Secure, scalable, maintainable full-stack AI design

---

## 🧭 System Architecture
```
Frontend (Next.js on Vercel)
│
├─ Chat Interface
│   ├─ Role selector or classifier
│   ├─ Chat input, feedback, and résumé/LinkedIn prompts
│   └─ Feedback and confession UI
│
├─ API Routes (Vercel Serverless)
│   ├─ /api/chat → Executes LangGraph workflow (RAG + role router)
│   ├─ /api/email → Sends résumé or LinkedIn link via Resend
│   ├─ /api/feedback → Logs rating, comments, contact requests
│   └─ /api/confess → Handles anonymous confessions
│
└─ LangGraph Workflow
    ├─ classify_intent → detect user type
    ├─ retrieve_context → pgvector retrieval from Supabase
    ├─ generate_answer → OpenAI (gpt-4o-mini)
    ├─ execute_tool → Email/SMS/log feedback
    └─ log_eval → store metrics (LangSmith optional)

Backend Services
├─ Supabase (Postgres + pgvector)
│   ├─ Tables: kb_chunks, messages, retrieval_logs, feedback, links, confessions, sms_logs
│   └─ Storage: résumé.pdf (private), headshot.jpg (public)
│
├─ OpenAI → embeddings + completions
├─ Resend → résumé/LinkedIn email
├─ Twilio → SMS alerts to Noah
└─ LangSmith → trace + evaluate
```

---

## 🧱 Tech Stack Summary
| Layer | Tool | Function |
|--------|------|----------|
| Frontend | Next.js (React) | Chat UI + role routing |
| Hosting | Vercel | Serverless deploys |
| Database | Supabase (Postgres + pgvector) | KB + analytics |
| LLM | OpenAI (gpt-4o-mini) | Response generation |
| Embeddings | OpenAI (text-embedding-3-small) | RAG vector search |
| Email | Resend API | Resume/LinkedIn delivery |
| SMS | Twilio | Notifications |
| Observability | LangSmith | Evaluation & trace |
| Orchestration | LangGraph | Multi-agent control |

---

## 🧠 LangGraph Workflow
Nodes:
1. **classify_intent:** Identify role_mode (nontech, tech, dev, exploring, confess)
2. **retrieve_context:** Query Supabase vector index
3. **generate_answer:** Produce grounded response (role-specific prompt)
4. **execute_tool:** Perform résumé/email/SMS action
5. **log_eval:** Write message, retrieval, feedback logs

Flow:
```
User → classify_intent → retrieve_context → generate_answer → execute_tool (if applicable) → log_eval
```

---

## 🗂️ Data Model
| Table | Purpose | Example Columns |
|--------|----------|----------------|
| kb_chunks | Embeddings of Noah’s KB | id, section, content, embedding |
| messages | Logs interactions | id, role_mode, query, answer, latency |
| retrieval_logs | Stores KB context metadata | message_id, topk_ids, scores |
| feedback | User ratings and contact requests | message_id, rating, comment, contact_requested |
| links | URL references | key, url |
| confessions | Confession records | is_anonymous, name, email, message |
| sms_logs | Notifications | event, timestamp, payload |

---

## 🎭 Roles & Capabilities

### 🧑‍💼 Hiring Manager (Non-Technical)
- Gives **career history**
- Offers **résumé or LinkedIn** after a few Qs
- Asks “Would you like Noah to reach out?” after sending
- Sends **SMS alert** on résumé/contact

### 🧑‍💻 Hiring Manager (Technical)
- Explains **project, stack, RAG, LangGraph**
- Describes **AI/software background**
- Explains **enterprise use of role routers**
- Provides **data schemas**
- Offers **résumé/LinkedIn**, asks about contact
- Sends **SMS on résumé/contact**

### 👨‍💻 Software Developer
- Details **architecture, data flow, and stack evolution**
- References **codebase snippets**
- Explains **enterprise scalability** and **LangGraph integration**

### 😎 Just Exploring
- Simple explanation of **project purpose**
- Shares **fun facts** (MMA, personal trivia)

### ❤️ Confess Crush
- Offers **anonymous or named confession**
- Sends **SMS** to Noah
- Stores confession securely

---

## 🧩 Data Collection Strategy
- **Every query** → `messages`
- **Each retrieval** → `retrieval_logs`
- **Feedback/contact** → `feedback` + SMS
- **Confession** → `confessions` + SMS
- **Résumé/LinkedIn send** → `sms_logs`
- Structured logging ensures reproducibility and observability.

---

## 💡 Development Philosophy
1. **Succinct File Structure**
   - Clear separation: `/core`, `/api`, `/services`, `/utils`
   - One purpose per file
2. **Readable Code**
   - Comment every function: What/Why/How
   - Avoid clever abstractions
3. **Efficiency**
   - Async I/O for DB, LLM, and APIs
   - Minimal caching for speed
4. **Junior-Friendly**
   - Easy to read top-to-bottom
   - Setup docs + env examples
5. **Observability**
   - Log metrics (latency, tokens, role_mode)
   - Integrate LangSmith traces

---

## ✅ Copilot Instructions
When writing code:
- Follow LangGraph flow (classify → retrieve → answer → tools → log)
- Use Supabase pgvector for retrieval (no FAISS)
- Respect role behaviors & tone
- Keep async/await structure
- Never expose secrets client-side
- Comment logic clearly for readability
- Write modular, efficient code approachable by new developers

---

## 📈 Summary Directive
> You are helping maintain Noah’s AI Assistant — a LangGraph-based, Supabase-backed RAG system that adapts to five user roles (hiring managers, developers, explorers, confessors). 
> Code should be succinct, modular, and well-commented, showing senior-level architecture and data handling while remaining clear and educational for junior developers.
