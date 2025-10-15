# Noah's AI Assistant

Noah's AI Assistant (repo: NoahsAIAssistant-) is a retrieval-augmented generative AI application that adapts its conversational style and retrieval strategy based on distinct user roles. It tailors responses for hiring managers, software developers, casual visitors, and personal interactions while emphasizing transparency, robustness, and compliance.

## Context Docs (Start Here)

This project ships with **self-documenting context** for Copilot and contributors.  
Open these when implementing features or refactoring so changes stay aligned:

### 🎯 Master Documentation (Authoritative)
- 📘 **Project Overview** → `docs/context/PROJECT_REFERENCE_OVERVIEW.md`  
  *Purpose, roles, stack, and behavior contracts*
- 🧩 **System Architecture** → `docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md`  
  *Control flow, RAG pipeline, data layer, presentation rules*
- 🧮 **Data & Schema Reference** → `docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md`  
  *Tables, queries, analytics, and grounding standards*
- 💬 **Conversation Personality** → `docs/context/CONVERSATION_PERSONALITY.md`  
  *Warmth, enthusiasm, invitation culture, and engagement style*

### 📚 Supplementary Guides
- `docs/GLOSSARY.md` - Technical definitions
- `docs/EXTERNAL_SERVICES.md` - Service setup (Resend, Twilio)
- `docs/OBSERVABILITY.md` - Metrics and monitoring
- `docs/LANGSMITH.md` - LangSmith tracing setup
- `docs/QUALITY_ASSURANCE_STRATEGY.md` - Testing strategy
- `docs/CONVERSATION_PIPELINE_MODULES.md` - Pipeline refactoring details

**Why:** These files define the assistant's purpose, stack, data contracts, and presentation rules (when to show code, data, or narrative). They are optimized for Copilot prompt context and human review.

## Table of Contents
- [🚀 Quickstart](#-quickstart)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Role-Specific Behaviors](#role-specific-behaviors)
- [Installation](#installation)
- [Usage](#usage)
- [LangGraph Flow](#langgraph-flow)
- [Platform Operations](#platform-operations)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Quickstart

**Get Noah's AI Assistant running locally in 5 minutes**

### Prerequisites
- ✅ Python 3.11+ installed
- ✅ OpenAI API key ([get one here](https://platform.openai.com/api-keys)) - $5 free credit for new accounts
- ✅ Supabase account ([sign up free](https://supabase.com/dashboard)) - Free tier is sufficient

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/noahcal/noahs-ai-assistant.git
cd noahs-ai-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
# Create a .env file with your API keys:
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...
```

**Get Supabase credentials**:
1. Create a new project in [Supabase Dashboard](https://supabase.com/dashboard)
2. Go to Settings → API
3. Copy `URL` and `service_role` key (⚠️ keep this secret!)

```bash
# 4. Set up the database schema
# Follow the step-by-step guide in archive/docs/migrated_from_docs/PHASE_1_SETUP.md
# This creates tables for knowledge base, messages, and analytics

# 5. Run the data migration (one-time)
python scripts/migrate_data_to_supabase.py

# 6. Start the Streamlit app
streamlit run src/main.py
```

**🎉 Success!** Open http://localhost:8501 in your browser.

**First steps**:
1. Select a role (try "Software Developer" to see code retrieval)
2. Ask a question like "What's your Python experience?"
3. See RAG in action with grounded responses!

**Need help?** See [PHASE_1_SETUP.md](docs/PHASE_1_SETUP.md) for detailed setup instructions.

**Next**: Explore the master docs in `docs/context/` or check out the [glossary](docs/GLOSSARY.md) for technical terms.

## Features
- **Role-Based Interaction**: Session-level role selection shapes retrieval + formatting.
- **Retrieval-Augmented Generation (RAG)**: Supabase pgvector stores (career KB, code index).
- **Dual-Audience Formatting**: Engineer Detail + Plain-English Summary (for technical audiences).
- **Code & Career Grounding**: File:line citations where available.
- **MMA Query Routing**: Direct fight link for MMA-related queries (bypasses general retrieval).
- **Confession Mode**: Lightweight, guarded input path with no unintended PII retention.
- **Analytics Tracking**: Interaction logging, retrieval tracking, user feedback with Supabase.
- **Contact Requests**: Email delivery via Resend, SMS notifications via Twilio.
- **Extensible Orchestration**: LangGraph-style node pipeline now powers the default flow.
- **Observability Ready**: LangSmith integration hooks (traces/evals).

## Tech Stack

### Current Architecture (Supabase + Vercel)
- **Frontend/UI**: Streamlit (chat UI, role selector, session management)
- **Core Framework**: LangChain (loaders, embeddings, retrieval pipeline)
- **Database**: Supabase Postgres with pgvector extension
- **Vector Search**: pgvector with IVFFLAT indexing for semantic similarity
- **Models**: OpenAI GPT-3.5/4 (generation), OpenAI ada-002 (embeddings)
- **Analytics**: Direct Supabase writes (messages, retrieval_logs, feedback)
- **External Services**: 
  - Resend (email delivery)
  - Twilio (SMS notifications)
- **API Layer**: Next.js API routes for external integrations
- **Security**: Row Level Security (RLS) policies, environment variables
- **Deployment**: Hybrid (Streamlit + Vercel serverless)
- **Observability**: LangSmith integration for tracing
- **Testing**: Pytest with Supabase mocking

### Cost Estimates
- **Supabase Pro**: ~$25/month (includes PostgreSQL + pgvector + Storage)
- **OpenAI API**: Variable based on usage (~$10-30/month for moderate traffic)
- **Vercel**: Free tier (serverless functions for API routes)
- **Resend**: Free tier up to 3,000 emails/month
- **Twilio**: Pay-as-you-go (~$0.0075/SMS)
- **Total**: ~$35-60/month for production deployment

**Previous GCP Architecture** (archived): Cost ~$100-200/month
- Used Cloud SQL, Pub/Sub, Secret Manager, Vertex AI, Cloud Run
- Migrated to Supabase for 50-75% cost reduction and simplified maintenance

## Role-Specific Behaviors

### 1. Hiring Manager (nontechnical)
- Goal: High-level résumé narrative
- Sources: Career KB CSV, résumé text
- Format: Career Overview → Notable Outcomes → Source Citations (lightweight)
- UI: Contact CTA (email / LinkedIn)

### 2. Hiring Manager (technical)
- Goal: Blend career signal + engineering depth
- Sources: Career KB + Code Index
- Format:
  - Section 1: Engineer Detail (with file:line citations)
  - Section 2: Plain-English Summary
- UI: Expandable code reference (future enhancement)

### 3. Software Developer
- Goal: Deep technical explanation, architecture, design tradeoffs
- Sources: Code Index + Career KB fallback
- Format: Engineer Detail → Summary (same dual format)

### 4. Just Looking Around
- Goal: Fun facts + MMA info
- MMA queries: Direct fight link
- Other queries: Light career / personal facts

### 5. Looking to Confess Crush
- Goal: Safe, minimal interaction channel
- Storage: Only explicit submission, no hidden PII retention
- Response: Acknowledgment only (no model overreach)

## Installation

### Prerequisites
- Python 3.10+
- Supabase account (free tier available)
- OpenAI API key
- (Optional) Resend API key for email
- (Optional) Twilio credentials for SMS

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/iNoahCodeGuy/NoahsAIAssistant-.git
cd NoahsAIAssistant-
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Supabase**
   - Create a new project at [supabase.com](https://supabase.com)
   - Run the SQL migration in `supabase/migrations/001_initial_schema.sql` in your Supabase SQL Editor
   - Copy your project URL and service role key

4. **Set environment variables**
```bash
cp .env.example .env
# Edit .env and add:
# SUPABASE_URL=your_project_url
# SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
# OPENAI_API_KEY=your_openai_key
# (Optional) RESEND_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM
```

5. **Populate knowledge base** (optional)
```bash
python scripts/migrate_data_to_supabase.py
```

## Usage

### Development
Run the Streamlit application locally:
```bash
streamlit run src/main.py
```

By default the LangGraph-inspired node pipeline runs. Set `LANGGRAPH_FLOW_ENABLED=false` only if you need the legacy `RoleRouter` path for troubleshooting (deprecated and scheduled for removal).

### Production Deployment

**Option 1: Streamlit Community Cloud**
- Deploy directly from GitHub
- Set environment variables in Streamlit Cloud dashboard
- Best for chat interface only

**Option 2: Hybrid (Streamlit + Vercel)**
- Deploy Streamlit for chat UI
- Deploy Next.js API routes to Vercel for email/SMS integrations
- Configure `vercel.json` for serverless functions

### Database Schema
The Supabase database includes:
- `kb_chunks`: Knowledge base with pgvector embeddings
- `messages`: Chat interaction logs
- `retrieval_logs`: RAG pipeline tracking
- `links`: External resource URLs
- `feedback`: User ratings and contact requests

### Architecture Overview
```
User → Streamlit UI → RagEngine (pgvector search) → OpenAI GPT → Response
                ↓
        Supabase Analytics (messages, retrieval_logs)
                ↓
        Feedback → Email (Resend) / SMS (Twilio)
```

## LangGraph Flow

- **Preferred Runtime:** `LANGGRAPH_FLOW_ENABLED=true` (default) executes `run_conversation_flow`, which chains `classify_query → retrieve_chunks → generate_answer → plan_actions → apply_role_context → execute_actions → log_and_notify` using `ConversationState`.
- **Legacy Path:** When the flag is `false`, the legacy `RoleRouter` handles requests. This path is frozen and will be removed once downstream integrations are migrated.
- **Service Initialization:** Conversation nodes lazily resolve Resend, Twilio, and Supabase Storage through shared helpers so both runtime and tests rely on the same singleton instances.
- **Inventory:** See `docs/runtime_dependencies.md` for the authoritative list of modules referenced at runtime.

## Platform Operations

- Consolidated observability, tracing, and monitoring guidance lives in `docs/platform_operations.md`.
- See `CONTRIBUTING.md` for full instructions.

- Contributor onboarding context (roles, architecture, data model) is captured in `docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md` and `docs/context/PROJECT_REFERENCE_OVERVIEW.md`.
- Legacy setup notes remain in `archive/docs` for historical reference when needed.

## File Structure
```
noahs-ai-assistant
├── src
│   ├── main.py
│   ├── config/
│   ├── core/
│   ├── retrieval/
│   ├── agents/
│   ├── ui/
│   ├── analytics/
│   └── utils/
├── data/
├── vector_stores/
├── tests/
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Contributing
1. Create a branch: feature/<name>
2. Keep commits focused
3. Open PR → request review

## License
MIT (see LICENSE if present). Add LICENSE file if not yet created.
