# Noah's AI Assistant

Noah's AI Assistant is an **educational generative AI application** that teaches users how GenAI systems work and their enterprise value by **using itself as a hands-on case study**. 

Through interactive conversation, it explains its own implementation—including RAG architecture, vector search, LLM orchestration, data pipelines, and system design—while demonstrating how these patterns can be adapted for enterprise use cases like customer support, internal documentation, and sales enablement.

**🎓 The Learning Approach**: Instead of abstract explanations, the assistant shows you the actual code, architecture diagrams, and data flows that power the conversation you're having. You can explore:
- "Show me the backend stack" → See real Python code with annotations
- "How does RAG work?" → Walk through the retrieval pipeline with examples
- "Display data analytics" → View live metrics and understand observability
- "What makes this valuable to enterprises?" → Connect technical patterns to business ROI

The assistant adapts its teaching style based on user roles (technical vs. non-technical), making complex AI concepts accessible while showcasing production-ready implementation patterns.

## Table of Contents
- [🚀 Quickstart](#-quickstart)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Role-Specific Behaviors](#role-specific-behaviors)
- [Installation](#installation)
- [Usage](#usage)
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
# Follow the step-by-step guide in docs/PHASE_1_SETUP.md
# This creates tables for knowledge base, messages, and analytics

# 5. Run the data migration (one-time)
python scripts/migrate_data_to_supabase.py

# 6. Start the Streamlit app
streamlit run src/main.py
```

**🎉 Success!** Open http://localhost:8501 in your browser.

**First steps**:
1. Select a role (try "Software Developer" to explore technical architecture)
2. Ask questions like:
   - "How does RAG work in this application?"
   - "Show me the backend architecture"
   - "Explain the data pipeline"
   - "What makes this valuable to enterprises?"
3. See the assistant explain its own implementation with code examples!

**Need help?** See [PHASE_1_SETUP.md](docs/PHASE_1_SETUP.md) for detailed setup instructions.

**Next**: Learn about [architecture](docs/ARCHITECTURE.md) or explore the [glossary](docs/GLOSSARY.md) for technical terms.

## What You'll Learn

Through interactive conversation, this assistant teaches you:

### For Technical Audiences
- **RAG Architecture**: How Retrieval-Augmented Generation works (vector embeddings, semantic search, context injection)
- **Vector Search**: Supabase pgvector implementation with IVFFLAT indexing and similarity scoring
- **LLM Orchestration**: LangGraph-style node-based conversation flows with state management
- **Data Pipelines**: Document processing, chunking strategies, embedding generation, and storage
- **System Design**: Hybrid deployment (Streamlit + Vercel), API routes, error handling, observability
- **Production Patterns**: Analytics logging, PII redaction, rate limiting, security (RLS policies)
- **Cost Optimization**: Model selection, caching strategies, and infrastructure choices
- **Testing & Reliability**: Pytest patterns, Supabase mocking, error degradation modes

### For Non-Technical Audiences
- **GenAI Business Value**: Why enterprises invest in AI assistants (cost savings, scalability, 24/7 availability)
- **Accuracy & Trust**: How RAG prevents hallucinations by grounding responses in real data
- **Data Governance**: PII protection, privacy controls, compliance considerations
- **ROI & Metrics**: Success measurement (response time, accuracy, user satisfaction, conversion rates)
- **Competitive Advantage**: Using AI to improve customer experience and operational efficiency
- **Implementation Roadmap**: High-level steps to build similar systems for your organization

### Live Demonstrations
The assistant demonstrates concepts by showing its own implementation:
- **Ask "show me the backend stack"** → See real Python code with explanations
- **Ask "display data analytics"** → Live dashboard with real-time metrics
- **Ask "how do you prevent hallucinations?"** → RAG pipeline walkthrough with examples
- **Ask "what's your data pipeline?"** → Document processing flow with architecture diagrams

## Features

### 🎓 Educational Features (Learn GenAI Through Demonstration)
- **Self-Referential Teaching**: Explains RAG, vector search, and LLM orchestration by showing its own implementation
- **Live Code Walkthroughs**: Displays actual Python files with explanations of GenAI patterns and enterprise applications
- **Architecture Tours**: Interactive exploration of stack, data pipelines, backend design, and deployment strategies
- **Enterprise Value Mapping**: Connects every technical concept to business ROI (cost reduction, scalability, reliability)
- **Role-Adaptive Teaching**: Adjusts depth for technical (with code) vs. non-technical (with analogies) audiences
- **Real Metrics Dashboard**: Shows live analytics to explain observability, logging, and data governance in production

### 🏗️ Technical Features (Production-Ready Patterns)
- **Retrieval-Augmented Generation (RAG)**: Supabase pgvector with IVFFLAT indexing for semantic search
- **LangGraph Orchestration**: Node-based conversation flows with immutable state management
- **Dual-Audience Formatting**: Technical details + plain-English summaries for mixed audiences
- **Code & Career Grounding**: File:line citations proving all responses are grounded in real data
- **PII Redaction**: Automated masking of emails/phones in user feedback (demonstrates data governance)
- **Rate Limiting**: 6 req/min per IP with graceful degradation (demonstrates production reliability)
- **Live Analytics Dashboard**: Real-time data visualization with PII redaction and role-based access
- **MMA Query Routing**: Direct fight link for MMA-related queries (demonstrates multi-modal routing)
- **Confession Mode**: Privacy-protected personal messaging (demonstrates data governance)
- **Analytics Tracking**: Interaction logging, retrieval tracking, user feedback with Supabase
- **Contact Requests**: Email delivery via Resend, SMS notifications via Twilio
- **Extensible Orchestration**: LangGraph-style node-based conversation flow
- **Observability**: LangSmith integration for tracing and performance monitoring

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
