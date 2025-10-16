# Documentation Audit Report
**Date:** October 14, 2025
**Status:** ⚠️ CONTRADICTIONS FOUND - ACTION REQUIRED

## Master Documentation (Source of Truth) ✅
Located in `docs/context/`:
1. PROJECT_REFERENCE_OVERVIEW.md - Purpose, roles, stack, behavior
2. SYSTEM_ARCHITECTURE_SUMMARY.md - Control flow, RAG pipeline, data layer
3. DATA_COLLECTION_AND_SCHEMA_REFERENCE.md - Tables, queries, presentation rules

## README and CONTRIBUTING ✅
Both correctly reference the master docs in `docs/context/`.

## Contradictory Files (NEED ACTION) ⚠️

### High Priority - Contradicts Master Docs:
1. **docs/ARCHITECTURE.md** (194 lines)
   - Contradiction: Shows old flow with "RoleRouter" + "Memory (session)"
   - Master says: LangGraph nodes (classify_intent → retrieve → answer)
   - Action: Archive or rewrite to match SYSTEM_ARCHITECTURE_SUMMARY.md

2. **docs/Copilot_Context_FullStack_LangGraph.md** (170 lines)
   - Contradiction: Different architecture description, mentions Next.js frontend
   - Master says: Streamlit for now, Vercel for API routes
   - Action: Archive (replaced by PROJECT_REFERENCE_OVERVIEW.md)

3. **docs/RAG_ENGINE.md** + **docs/RAG_ENGINE_STRUCTURE.md**
   - Contradiction: May describe old FAISS-based system
   - Master says: pgvector only
   - Action: Review and archive if outdated

### Medium Priority - May Be Outdated:
4. **docs/enterprise_readiness_playbook.md**
   - Status: Check if aligns with SYSTEM_ARCHITECTURE_SUMMARY section 7
   - Action: Verify or archive

5. **docs/REQUIREMENTS_ALIGNMENT.md**
   - Status: May be legacy requirement tracking
   - Action: Archive if no longer used

### Low Priority - Supplementary Docs (OK to Keep):
6. **docs/GLOSSARY.md** - Definitions (useful reference)
7. **docs/EXTERNAL_SERVICES.md** - Service setup (useful)
8. **docs/LANGSMITH.md** - Observability guide (useful)
9. **docs/OBSERVABILITY.md** - Metrics guide (useful)
10. **docs/QUALITY_ASSURANCE_STRATEGY.md** - Testing strategy (useful)
11. **docs/CONVERSATION_PIPELINE_MODULES.md** - NEW, aligns with refactoring (keep)
12. **docs/platform_operations.md** - Ops guide (keep)
13. **docs/runtime_dependencies.md** - Dependencies (keep)

## Recommended Actions:

### Phase 1: Archive Contradictory Docs
Move these to `docs/archive/`:
- ARCHITECTURE.md
- Copilot_Context_FullStack_LangGraph.md
- RAG_ENGINE.md (if outdated)
- RAG_ENGINE_STRUCTURE.md (if outdated)
- enterprise_readiness_playbook.md (if superseded)
- REQUIREMENTS_ALIGNMENT.md (if no longer used)

### Phase 2: Create Reference Guide
Add to README.md:
```markdown
## Documentation Structure

### 🎯 Start Here (Master Docs)
- Project Overview → `docs/context/PROJECT_REFERENCE_OVERVIEW.md`
- System Architecture → `docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md`
- Data & Schema → `docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md`

### 📚 Supplementary Guides
- Glossary → `docs/GLOSSARY.md`
- External Services → `docs/EXTERNAL_SERVICES.md`
- Observability → `docs/OBSERVABILITY.md`
- LangSmith Setup → `docs/LANGSMITH.md`
- QA Strategy → `docs/QUALITY_ASSURANCE_STRATEGY.md`
- Pipeline Modules → `docs/CONVERSATION_PIPELINE_MODULES.md`
```

### Phase 3: Update .github/copilot-instructions.md
Ensure it only references master docs in `docs/context/`.
