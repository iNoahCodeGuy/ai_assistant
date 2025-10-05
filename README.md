# Noah's AI Assistant

Noah's AI Assistant (repo: NoahsAIAssistant-) is a retrieval-augmented generative AI application that adapts its conversational style and retrieval strategy based on distinct user roles. It tailors responses for hiring managers, software developers, casual visitors, and personal interactions while emphasizing transparency, robustness, and compliance.

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Role-Specific Behaviors](#role-specific-behaviors)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Role-Based Interaction**: Session-level role selection shapes retrieval + formatting.
- **Retrieval-Augmented Generation (RAG)**: Supabase pgvector stores (career KB, code index).
- **Dual-Audience Formatting**: Engineer Detail + Plain-English Summary (for technical audiences).
- **Code & Career Grounding**: File:line citations where available.
- **MMA Query Routing**: Direct fight link for MMA-related queries (bypasses general retrieval).
- **Confession Mode**: Lightweight, guarded input path with no unintended PII retention.
- **Analytics Tracking**: Interaction logging, retrieval tracking, user feedback with Supabase.
- **Contact Requests**: Email delivery via Resend, SMS notifications via Twilio.
- **Extensible Orchestration**: Designed to plug into LangGraph for future routing graphs.
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
