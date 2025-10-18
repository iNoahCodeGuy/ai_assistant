# Changelog

All notable changes to Portfolia (Noah's AI Assistant) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project follows calendar-based versioning.

---

## [Unreleased]

### Added
- **Documentation Consolidation Policy (Section 12)** - Added to `docs/QA_STRATEGY.md` to prevent future QA documentation sprawl with decision tree, file categorization rules, and quarterly review process
- **Intelligent Resume Distribution System (COMPLETE)**: Hybrid approach for converting hiring manager education into opportunities
  - **Mode 1 (Pure Education)**: ZERO resume mentions - maintains educational focus
  - **Mode 2 (Hiring Signals)**: ONE subtle availability mention when ≥2 hiring signals detected + HM role
  - **Mode 3 (Explicit Request)**: Immediate email collection and resume distribution (no qualification needed)
  - **Job Details Gathering**: Post-interest conversational extraction (company, position, timeline)
  - **Implementation**: 9 functions in `src/flows/resume_distribution.py` (343 lines)
  - **Integration**: Added to conversation pipeline via `extract_job_details_from_query` node
  - **External Services**: Email via Resend, SMS via Twilio with job details
  - **Test Coverage**: 37 automated tests (100% pass rate in 0.04s)
  - **Documentation**:
    - Feature doc: `docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md`
    - Master docs updated: `SYSTEM_ARCHITECTURE_SUMMARY.md`, `PROJECT_REFERENCE_OVERVIEW.md`
    - QA standards: `QA_STRATEGY.md` Section 1.1-1.2
  - **Status**: ✅ COMPLETE - Ready for Streamlit testing

### Changed
- **QA Documentation Consolidated**: Merged 5 separate QA docs into single source of truth
  - Merged LangSmith Phase 2 content into `docs/QA_STRATEGY.md` Section 9
  - Archived historical policy docs to `docs/archive/policies/`
  - Archived task-specific reports to `docs/archive/deployments/`
  - Archived analysis docs to `docs/archive/analysis/`
  - Added Section 12: Documentation Consolidation Policy to prevent future sprawl
  - Result: 1 master QA doc (3,200 lines) replacing 5 files (4,620 lines, ~1,400 duplication)
- **QA Test Suite Expanded**: 71 total tests (was 31 tests)
  - Conversation Quality: 19 tests (100% pass rate) - Added `test_no_pushy_resume_offers()`
  - Documentation Alignment: 15 tests (93% pass rate) - Added 3 resume distribution alignment tests
  - Resume Distribution: 37 tests (100% pass rate) - Comprehensive hybrid approach validation
  - **Pass Rate**: 99% overall (70/71 passing, 1 intentionally skipped)

- **Conversation Pipeline Extended**: Added `extract_job_details_from_query` node
  - Runs after `classify_query` to extract job details post-interest
  - Updated flow: `handle_greeting → classify → extract_job_details → retrieve → generate → plan → apply → execute → log`

- **Conversation State Extended**: 6 new fields for resume distribution
  - `hiring_signals`: List tracking passive signals (mentioned_hiring, described_role, team_context)
  - `resume_explicitly_requested`: Boolean flag for Mode 3 detection
  - `resume_sent`: Once-per-session enforcement flag
  - `user_email`: Collected email address
  - `user_name`: Collected name (with fallback)
  - `job_details`: Dict with company, position, timeline (post-interest)

### Technical
- **Files Modified/Created**: 13+ files across feature implementation, testing, documentation
- **Code Quality**: All regex patterns validated through test-driven development (5 iterations)
- **Service Integration**: Graceful degraded mode handling for Resend/Twilio failures
- **Observability**: All resume send actions logged to Supabase with analytics tracking

### Fixed
### Deprecated

---

## [2025-10-16] - Q&A Synthesis Enforcement

### Fixed
- **Q&A Verbatim Bug**: Prevented knowledge base Q&A format from being returned verbatim in responses
  - Added synthesis instructions to all 3 role prompts (Technical HM, Software Developer, General)
  - Updated master documentation (DATA_COLLECTION_AND_SCHEMA_REFERENCE.md) with synthesis rules
  - Added 2 automated tests to prevent regression (test_no_qa_verbatim_responses, test_response_synthesis_in_prompts)
  - **Impact**: Users now receive natural conversational responses instead of raw "Q: ... A: ..." format
  - **Technical details**: See `QA_POLICY_UPDATE_NO_QA_VERBATIM.md` (will be archived after verification)
  - **Commit**: 0327e5e

---

## [2025-10-15] - Proactive Display Intelligence

### Added
- **Proactive Code Display**: Technical roles now receive code snippets even when not explicitly requesting them
  - Triggers on queries about RAG, vector search, orchestration, architecture patterns
  - Only for Software Developer and Hiring Manager (technical) roles
  - Code snippets include explanatory comments and design rationale
- **Proactive Data Display**: Analytics/metrics shown when queries imply measurements
  - Triggers on "how many", "how much", "performance", "trend" queries
  - Applies to all roles (metrics help everyone understand)
  - Data includes source attribution and context
- **Implementation**: Enhanced query classification in `src/flows/query_classification.py`
- **Documentation**: See `PROACTIVE_DISPLAY_SUMMARY.md` (will be consolidated into `docs/features/DISPLAY_INTELLIGENCE.md`)
- **Commit**: 5718ff4

---

## [2025-10-15] - Display Intelligence Foundation

### Added
- **Teaching Moment Detection**: System now recognizes when users need longer, more detailed explanations
  - Triggers on "why", "how", "explain", "walk me through" queries
  - Adjusts response depth and structure accordingly
- **Explicit Code Display**: Handles direct requests to "show code" or "display implementation"
  - Preserves formatting, includes context, explains GenAI patterns
- **Explicit Data Display**: Handles requests for analytics, metrics, statistics
  - Professional markdown tables, source attribution
- **Query Classification Enhancement**: Added detection for teaching moments, code requests, data requests
- **LLM Prompt Enhancement**: Dynamic instruction injection based on query type
- **Implementation**: Modified `src/flows/query_classification.py` and `src/flows/core_nodes.py`
- **Documentation**: See `DISPLAY_INTELLIGENCE_IMPLEMENTATION.md` (will be consolidated)
- **Commit**: 1d9fdc4

---

## [2025-10-15] - Portfolia Branding Update

### Changed
- **Frontend Branding**: Updated Next.js application to display "Portfolia" instead of "Noah's AI Assistant"
  - Changed header, metadata, page titles
  - Maintains brand consistency with Streamlit version
- **Files Modified**: `frontend/app/page.tsx`, metadata configurations
- **Commit**: ffb95b5

---

## [2025-10-15] - Master Documentation Implementation

### Added
- **Master Documentation Framework**: Created 4 authoritative source-of-truth documents in `docs/context/`
  - `PROJECT_REFERENCE_OVERVIEW.md`: Purpose, value, stack, roles, behavior
  - `SYSTEM_ARCHITECTURE_SUMMARY.md`: Architecture, control flow, RAG pipeline
  - `DATA_COLLECTION_AND_SCHEMA_REFERENCE.md`: Data contracts, presentation rules
  - `CONVERSATION_PERSONALITY.md`: Teaching persona, tone, engagement patterns
- **GitHub Copilot Instructions**: Comprehensive `.github/copilot-instructions.md` referencing master docs
- **Impact**: Centralized system knowledge, improved AI assistant context, enforced single source of truth

---

## [2025-10-14] - Complete System as Case Study

### Added
- **Comprehensive Learning Guide**: Created `docs/LEARNING_GUIDE_COMPLETE_SYSTEM.md` (800+ lines)
  - Covers frontend, backend, data pipeline, system architecture, QA, DevOps
  - Includes code examples, enterprise mapping, exploration queries
  - Teaches GenAI concepts using Portfolia itself as the case study
- **System-Wide Teaching Enhancement**: Assistant now explicitly teaches ALL components
  - Frontend development patterns
  - Backend architecture patterns
  - Data pipeline management
  - RAG and vector search
  - Testing strategies
  - Deployment and cost optimization

---

## [2025-10-13] - Conversation Personality Enhancement

### Added
- **Warmth and Enthusiasm**: Enhanced greeting system with genuine excitement
  - "Hey! 👋 I'm really excited you're here..."
  - Role-specific menu of conversation starters
  - Explicit invitation to ask about GenAI internals
- **Teaching-Focused Persona**: Reinforced educational mission throughout conversations
  - Emphasis on teaching how GenAI applications work
  - Connection between technical patterns and business value
  - Progressive depth based on user curiosity
- **Implementation**: Updated greeting templates in `src/flows/content_blocks.py`

---

## [2025-10-10] - Role-Based Conversation Flow

### Added
- **5 Distinct User Roles**: Each with tailored behavior and content
  - Hiring Manager (technical): Business + technical hybrid
  - Hiring Manager (nontechnical): Business-focused explanations
  - Software Developer: Deep architecture dives with code
  - Just looking around: Friendly GenAI tour
  - Confess (fun easter egg): Anonymous message system
- **Role-Specific Features**: Differential code display, technical depth, tone
- **Implementation**: See `ROLE_FEATURES.md` for complete specifications

---

## [2025-10-08] - LangGraph Modular Pipeline

### Added
- **Node-Based Conversation Flow**: Replaced monolithic processing with modular nodes
  - `classify_query` → `retrieve_chunks` → `generate_answer` → `plan_actions` → `apply_role_context` → `execute_actions` → `log_and_notify`
  - Each node handles single responsibility
  - Immutable state updates via `ConversationState` dataclass
- **Modular File Structure**: Separated concerns into focused modules
  - `conversation_nodes.py`: Core pipeline (311 lines)
  - `content_blocks.py`: Reusable messaging blocks (127 lines)
  - `data_reporting.py`: Analytics display (172 lines)
  - `action_execution.py`: Side effects handler (222 lines)
- **Benefits**: Easier testing, clearer logic flow, better maintainability
- **Documentation**: See `docs/CONVERSATION_PIPELINE_MODULES.md`

---

## [2025-10-05] - Vercel Production Deployment

### Added
- **Serverless API Endpoints**: 4 Vercel function routes
  - `/api/chat`: Main conversation endpoint
  - `/api/email`: Contact/resume requests
  - `/api/feedback`: User feedback collection
  - `/api/confess`: Anonymous message submission
- **Hybrid Deployment**: Streamlit for local dev + Vercel for production
- **Environment Detection**: Automatic behavior adjustment based on deployment context
- **Configuration**: `vercel.json` with Python runtime settings

---

## [2025-10-01] - Supabase pgvector Migration

### Changed
- **Vector Storage**: Migrated from local FAISS to Supabase pgvector
  - Centralized vector storage in Postgres
  - Production-ready reliability
  - Eliminated local file dependencies
- **Data Migration**: One-time script to populate pgvector with existing knowledge base
  - Idempotent by content hash
  - Automated embedding generation
- **Retrieval Enhancement**: `src/retrieval/pgvector_retriever.py` with similarity search
- **Cost**: Minimal (~$25/month Supabase tier)

---

## [2025-09-28] - Initial RAG Implementation

### Added
- **RAG Engine**: Core retrieval-augmented generation pipeline
  - Knowledge base ingestion from CSV
  - Text chunking (500 tokens, 50 overlap)
  - OpenAI embeddings (text-embedding-3-small, 768 dims)
  - Semantic similarity search
  - Context-aware LLM generation (GPT-4o-mini)
- **Knowledge Bases**: 3 initial CSVs
  - `career_kb.csv`: Noah's professional background (27 Q&A pairs)
  - `technical_kb.csv`: Technical implementation details
  - `architecture_kb.csv`: System architecture explanations
- **Analytics Foundation**: Supabase tables for logging
  - `messages`: Conversation history
  - `retrieval_logs`: RAG pipeline performance
  - `feedback`: User ratings and comments

---

## [2025-09-25] - Project Initialization

### Added
- **Streamlit Interface**: Initial chat UI with role selection
- **OpenAI Integration**: GPT-4o-mini for response generation
- **Basic Conversation**: Simple prompt-response without RAG
- **Repository Setup**: Initial project structure, requirements.txt, README
- **Purpose**: Interactive résumé assistant demonstrating GenAI concepts

---

## Legend

**[YYYY-MM-DD]** - Release/feature date
**Added** - New features
**Changed** - Changes to existing functionality
**Fixed** - Bug fixes
**Deprecated** - Features marked for removal
**Removed** - Deleted features
**Security** - Security-related changes

---

## Documentation

For detailed implementation notes on specific features, see:
- **Features**: `docs/features/` directory
- **Bug Fixes**: `docs/archive/bugfixes/` directory
- **Implementation Reports**: `docs/implementation/` directory
- **Design Decisions**: `docs/DESIGN_DECISIONS.md`

For system architecture and behavior, see:
- **Master Documentation**: `docs/context/` directory (source of truth)
