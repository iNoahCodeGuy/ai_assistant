# Required Reading for AI Assistants

**Format**: Machine-readable document manifest
**Last Updated**: October 19, 2025
**Purpose**: Defines which documents to load for different development tasks

---

## Document Format

```
PRIORITY|filepath|use_case|key_sections|auto_load_triggers
```

**Priority Levels**:
- `CRITICAL` - Always load (Tier 1)
- `HIGH` - Daily reference (Tier 2)
- `MEDIUM` - Feature-specific (Tier 3)
- `LOW` - Optional reference (Tier 4)

---

## Tier 1: Always Load (Master Docs)

```
CRITICAL|docs/context/PROJECT_REFERENCE_OVERVIEW.md|product_vision|roles,tech_stack,value_prop,educational_mission|all
CRITICAL|docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md|architecture|control_flow,rag_pipeline,deployment,langgraph_nodes|all
CRITICAL|docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md|data_layer|tables,queries,presentation_rules,grounding|all
CRITICAL|docs/context/CONVERSATION_PERSONALITY.md|tone|personality_traits,ask_mode,greetings,role_openings|all
```

**When to Load**: Every development task, architecture decision, feature implementation

**Why Critical**:
- Defines product identity (what Portfolia IS)
- Shows system flow (how everything connects)
- Establishes data contracts (source of truth)
- Sets conversation tone (user experience)

---

## Tier 2: Daily Reference (Development)

```
HIGH|CONTINUE_HERE.md|project_status|current_tests,next_actions,recent_progress,known_issues|feature,test,deploy
HIGH|docs/QA_STRATEGY.md|testing|design_principles,langgraph_patterns,qa_checklist,test_categories|test,deploy,architecture
HIGH|.github/copilot-instructions.md|conventions|import_patterns,service_pattern,anti_patterns,common_workflows|feature,test
HIGH|docs/LANGGRAPH_ALIGNMENT.md|architecture_decisions|current_state,migration_path,best_practices_comparison|architecture,feature
HIGH|WEEK_1_LAUNCH_GAMEPLAN.md|execution_plan|daily_tasks,success_criteria,deployment_steps|deploy
```

**When to Load**: Daily work, implementing features, fixing bugs, making PRs

**Why High Priority**:
- Current status (what's done, what's next)
- Quality standards (how to build correctly)
- Coding conventions (project-specific patterns)
- Architecture roadmap (what's stable, what's changing)

---

## Tier 3: Feature-Specific (On-Demand)

```
MEDIUM|docs/ROLE_FEATURES.md|role_behaviors|5_roles,knowledge_access,resume_modes,conversation_styles|feature,role
MEDIUM|docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md|resume_feature|3_tier_model,signal_detection,email_sms_integration|feature,role
MEDIUM|docs/RAG_ENGINE.md|rag_internals|class_structure,retrieval_methods,generation_pipeline|feature,architecture
MEDIUM|docs/EXTERNAL_SERVICES.md|integrations|twilio,resend,supabase_patterns,storage|feature,deploy
MEDIUM|docs/features/ANALYTICS_IMPLEMENTATION.md|analytics|data_contracts,table_formatting,visualization,privacy|feature
MEDIUM|docs/features/ERROR_HANDLING_IMPLEMENTATION.md|resilience|graceful_degradation,fallback_strategies,service_patterns|feature,test
MEDIUM|docs/platform_operations.md|observability|langsmith,tracing,monitoring,cost_control|deploy,architecture
```

**When to Load**: Implementing specific features, debugging domain-specific issues

**Why Medium Priority**:
- Feature-specific details (not needed for all tasks)
- Domain expertise (role logic, integrations, observability)
- Implementation patterns (error handling, analytics)

---

## Tier 4: Reference Only (Optional)

```
LOW|README.md|overview|installation,quick_start,tech_stack_summary|onboarding
LOW|CHANGELOG.md|history|recent_changes,version_tracking|onboarding,deploy
```

**When to Load**: Onboarding, stakeholder communication, historical reference

**Why Low Priority**:
- High-level overviews (less detail than master docs)
- Historical tracking (changes over time)
- Public-facing documentation (README for external users)

---

## Auto-Load Triggers

### Trigger: `feature` (Implementing New Features)

**Auto-Load**:
- Tier 1 (all 4 master docs)
- `CONTINUE_HERE.md` (current status)
- `docs/QA_STRATEGY.md` (design principles, testing)
- `.github/copilot-instructions.md` (conventions)
- `docs/ROLE_FEATURES.md` (if role-related)
- `docs/features/[RELATED_FEATURE].md` (if similar feature exists)

**Command**: `./.copilot/scripts/load_context.sh feature`

---

### Trigger: `test` (Fixing Tests, TDD)

**Auto-Load**:
- Tier 1 (all 4 master docs)
- `docs/QA_STRATEGY.md` (testing philosophy, patterns)
- `.github/copilot-instructions.md` (mocking patterns, service factories)
- `CONTINUE_HERE.md` (current test status)
- `docs/features/ERROR_HANDLING_IMPLEMENTATION.md` (error handling tests)

**Command**: `./.copilot/scripts/load_context.sh test`

---

### Trigger: `deploy` (Production Deployment)

**Auto-Load**:
- Tier 1 (all 4 master docs)
- `WEEK_1_LAUNCH_GAMEPLAN.md` (deployment checklist)
- `docs/platform_operations.md` (monitoring, LangSmith)
- `docs/LANGGRAPH_ALIGNMENT.md` (architecture stability)
- `docs/QA_STRATEGY.md` (pre-launch QA checklist)
- `docs/EXTERNAL_SERVICES.md` (service configuration)

**Command**: `./.copilot/scripts/load_context.sh deploy`

---

### Trigger: `architecture` (Architecture Decisions)

**Auto-Load**:
- Tier 1 (all 4 master docs)
- `docs/LANGGRAPH_ALIGNMENT.md` (current vs best practices)
- `docs/QA_STRATEGY.md` (design principles)
- `docs/RAG_ENGINE.md` (RAG implementation)
- `docs/ARCHITECTURE.md` (legacy reference)

**Command**: `./.copilot/scripts/load_context.sh architecture`

---

### Trigger: `role` (Role-Specific Behavior)

**Auto-Load**:
- Tier 1 (all 4 master docs)
- `docs/ROLE_FEATURES.md` (5 role definitions)
- `docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md` (resume modes)
- `docs/context/CONVERSATION_PERSONALITY.md` (tone per role)

**Command**: `./.copilot/scripts/load_context.sh role`

---

### Trigger: `default` (General Development)

**Auto-Load**:
- Tier 1 (all 4 master docs)
- `CONTINUE_HERE.md` (current status)
- `.github/copilot-instructions.md` (conventions)

**Command**: `./.copilot/scripts/load_context.sh` (no argument)

---

## Context Rules (For AI Assistants)

### Rule 1: Always Start with Tier 1
Before generating any code, architecture decisions, or recommendations:
1. Read all 4 Tier 1 docs
2. Understand product vision, system flow, data contracts, tone
3. Reference these throughout the conversation

### Rule 2: Load Task-Specific Context
Based on user's request, load appropriate Tier 2/3 docs:
- "implement feature" → feature trigger
- "fix tests" → test trigger
- "deploy" → deploy trigger
- "architecture decision" → architecture trigger

### Rule 3: Cite Your Sources
When referencing information:
- Mention which doc it came from
- Include section name if relevant
- Example: "According to SYSTEM_ARCHITECTURE_SUMMARY.md (Control Flow section)..."

### Rule 4: Verify Context Freshness
- Check `CONTINUE_HERE.md` for current status
- If doc mentions "Last Updated" > 30 days ago, flag as potentially stale
- Recommend user verify critical details

### Rule 5: Request Missing Context
If task requires doc not yet loaded:
- List which additional docs would help
- Explain why they're relevant
- Ask user if you should load them

---

## Document Health Checks

### Verify All Docs Exist
```bash
python .copilot/scripts/verify_context.py
```

### Check for Broken Links
```bash
# Find all markdown links
grep -r "\[.*\](.*\.md)" docs/

# Verify each file exists
for file in $(grep -roh "(\S+\.md)" docs/ | tr -d '()'); do
  [ -f "$file" ] || echo "Missing: $file"
done
```

### Find Orphaned Docs
```bash
# Find docs not referenced in REQUIRED_READING.md
comm -23 \
  <(find docs/ -name "*.md" | sort) \
  <(grep -o "docs/[^|]*\.md" .copilot/REQUIRED_READING.md | sort)
```

---

## Maintenance Schedule

### Weekly
- [ ] Run `verify_context.py` to check for broken links
- [ ] Update `CONTINUE_HERE.md` with current status
- [ ] Review Tier 2 docs for accuracy

### Monthly
- [ ] Review priority levels (promote/demote based on usage)
- [ ] Archive outdated docs to `docs/archive/`
- [ ] Update auto-load triggers if new patterns emerge

### Per Feature Launch
- [ ] Update relevant feature docs
- [ ] Add new docs to manifest if created
- [ ] Update `CHANGELOG.md` with doc changes

---

## Examples

### Example 1: Implementing Resume Download Feature

**User asks**: "I need to add a download resume button"

**AI should load**:
- Tier 1 (always)
- `docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md` (resume feature)
- `docs/EXTERNAL_SERVICES.md` (Supabase Storage for resume URLs)
- `docs/QA_STRATEGY.md` (design principles, testing)

**Rationale**: Resume-related feature needs resume distribution context + storage patterns

---

### Example 2: Fixing Failing Tests

**User asks**: "Tests in test_error_handling.py are failing"

**AI should load**:
- Tier 1 (always)
- `docs/QA_STRATEGY.md` (testing philosophy, patterns)
- `.github/copilot-instructions.md` (mocking patterns)
- `docs/features/ERROR_HANDLING_IMPLEMENTATION.md` (what those tests verify)

**Rationale**: Error handling tests need context on error handling standards + mocking conventions

---

### Example 3: Architecture Decision - StateGraph Migration

**User asks**: "Should we migrate to StateGraph now or wait?"

**AI should load**:
- Tier 1 (always)
- `docs/LANGGRAPH_ALIGNMENT.md` (migration plan, current state)
- `docs/QA_STRATEGY.md` (design principles, risk assessment)
- `WEEK_1_LAUNCH_GAMEPLAN.md` (Week 1 stability priority)

**Rationale**: Architecture decision needs current architecture + migration roadmap + launch timeline

---

## Notes for AI Assistants

### When Context is Ambiguous
- Default to Tier 1 + CONTINUE_HERE.md
- Ask user which specific area they're working on
- Suggest relevant Tier 2/3 docs based on keywords

### When Multiple Docs Conflict
- Tier 1 > Tier 2 > Tier 3 > Tier 4 (trust hierarchy)
- `CONTINUE_HERE.md` overrides historical docs (most current)
- `.github/copilot-instructions.md` overrides general docs (project-specific)

### When Docs are Missing
- Flag missing doc to user
- Suggest creating it if needed repeatedly
- Work with available context, note limitations

### When Context Exceeds Token Limit
- Prioritize Tier 1 (non-negotiable)
- Load only relevant sections of Tier 2/3
- Summarize Tier 4 instead of full text

---

**Machine-Readable Section Below** (for programmatic parsing)

```json
{
  "manifest_version": "1.0",
  "last_updated": "2025-10-19",
  "tier_1_docs": [
    "docs/context/PROJECT_REFERENCE_OVERVIEW.md",
    "docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md",
    "docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md",
    "docs/context/CONVERSATION_PERSONALITY.md"
  ],
  "tier_2_docs": [
    "CONTINUE_HERE.md",
    "docs/QA_STRATEGY.md",
    ".github/copilot-instructions.md",
    "docs/LANGGRAPH_ALIGNMENT.md",
    "WEEK_1_LAUNCH_GAMEPLAN.md"
  ],
  "auto_load_mappings": {
    "feature": ["tier_1", "CONTINUE_HERE.md", "docs/QA_STRATEGY.md", ".github/copilot-instructions.md"],
    "test": ["tier_1", "docs/QA_STRATEGY.md", ".github/copilot-instructions.md", "CONTINUE_HERE.md"],
    "deploy": ["tier_1", "WEEK_1_LAUNCH_GAMEPLAN.md", "docs/platform_operations.md", "docs/LANGGRAPH_ALIGNMENT.md"],
    "architecture": ["tier_1", "docs/LANGGRAPH_ALIGNMENT.md", "docs/QA_STRATEGY.md", "docs/RAG_ENGINE.md"],
    "role": ["tier_1", "docs/ROLE_FEATURES.md", "docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md"],
    "default": ["tier_1", "CONTINUE_HERE.md", ".github/copilot-instructions.md"]
  }
}
```
