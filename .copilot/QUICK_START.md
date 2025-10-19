# 🚀 Quick Start - AI Context for Developers

**Purpose**: One-page reference for loading context when working with AI assistants

**Last Updated**: October 19, 2025

---

## ⚡ TL;DR - Common Commands

```bash
# Load context for implementing features
./.copilot/scripts/load_context.sh feature

# Load context for fixing tests
./.copilot/scripts/load_context.sh test

# Load context for deployment
./.copilot/scripts/load_context.sh deploy

# Load default context (general work)
./.copilot/scripts/load_context.sh
```

---

## 📚 The 4 Master Docs (Always Read First)

1. **[`docs/context/PROJECT_REFERENCE_OVERVIEW.md`](../docs/context/PROJECT_REFERENCE_OVERVIEW.md)**
   - What Portfolia is, who uses it, why it exists
   - 5 user roles, tech stack, value proposition

2. **[`docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md`](../docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md)**
   - How the system works, data flow
   - LangGraph pipeline, RAG architecture

3. **[`docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md`](../docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md)**
   - Database schemas, queries, data contracts
   - Supabase tables, presentation rules

4. **[`docs/context/CONVERSATION_PERSONALITY.md`](../docs/context/CONVERSATION_PERSONALITY.md)**
   - How Portfolia talks, conversation tone
   - Role-specific greetings, ask mode behaviors

---

## 🎯 Quick Reference by Task

### Implementing a New Feature
```bash
# 1. Load context
./.copilot/scripts/load_context.sh feature

# 2. Read these docs:
# - The 4 master docs (above)
# - docs/QA_STRATEGY.md (design principles, testing)
# - .github/copilot-instructions.md (coding conventions)
# - docs/ROLE_FEATURES.md (if role-related feature)

# 3. Use template
cat .copilot/templates/implement_feature.md
# Copy into AI chat, fill in [FEATURE_NAME]
```

### Fixing Failing Tests
```bash
# 1. Load context
./.copilot/scripts/load_context.sh test

# 2. Read these docs:
# - docs/QA_STRATEGY.md (testing philosophy)
# - .github/copilot-instructions.md (mocking patterns)
# - CONTINUE_HERE.md (current test status)

# 3. Use template
cat .copilot/templates/fix_tests.md
# Copy into AI chat, fill in [TEST_FILE]
```

### Deploying to Production
```bash
# 1. Load context
./.copilot/scripts/load_context.sh deploy

# 2. Read these docs:
# - WEEK_1_LAUNCH_GAMEPLAN.md (deployment steps)
# - docs/platform_operations.md (monitoring)
# - docs/QA_STRATEGY.md (pre-launch checklist)

# 3. Use template
cat .copilot/templates/deploy_production.md
# Work through checklist with AI
```

### Making Architecture Decisions
```bash
# 1. Load context
./.copilot/scripts/load_context.sh architecture

# 2. Read these docs:
# - docs/LANGGRAPH_ALIGNMENT.md (current vs best practices)
# - docs/QA_STRATEGY.md (design principles)
# - docs/RAG_ENGINE.md (RAG implementation)

# 3. Use template
cat .copilot/templates/architecture_decision.md
# Copy into AI chat, fill in [TOPIC]
```

---

## 📋 Conversation Templates

All templates in `.copilot/templates/`:

| Template | Use When | Key Sections |
|----------|----------|--------------|
| `implement_feature.md` | Building new functionality | Plan, tests, docs |
| `fix_tests.md` | Debugging test failures | Root cause, fix, verify |
| `deploy_production.md` | Deploying to Vercel/Streamlit | Pre-flight, deploy, smoke test |
| `architecture_decision.md` | Choosing tech/patterns | Options, analysis, recommendation |
| `code_review.md` | Reviewing PRs | Design principles, testing, alignment |

---

## 🧭 Navigation Cheat Sheet

### When You're Lost
1. Read: `CONTINUE_HERE.md` (current status, next steps)
2. Read: `.copilot/README.md` (this folder's purpose)
3. Read: The 4 master docs (foundation)

### When You Need Coding Standards
1. Read: `docs/QA_STRATEGY.md` (8 design principles)
2. Read: `.github/copilot-instructions.md` (project conventions)
3. Check: `.copilot/templates/code_review.md` (checklist)

### When You Need Architecture Context
1. Read: `docs/LANGGRAPH_ALIGNMENT.md` (current state + migration)
2. Read: `docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md` (how it works)
3. Check: `WEEK_1_LAUNCH_GAMEPLAN.md` (Week 1 stability priority)

### When You Need Feature Context
1. Read: `docs/ROLE_FEATURES.md` (5 role behaviors)
2. Read: `docs/features/[FEATURE_NAME].md` (if exists)
3. Check: `docs/context/CONVERSATION_PERSONALITY.md` (tone/voice)

---

## ✅ Before Starting Any Work

**5-Minute Checklist**:
- [ ] Read `CONTINUE_HERE.md` (what's the current status?)
- [ ] Run `./.copilot/scripts/load_context.sh [mode]` (load relevant docs)
- [ ] Skim the 4 master docs (refresh on product/architecture)
- [ ] Check `docs/QA_STRATEGY.md` design principles (how to build it right)
- [ ] Get conversation template (use AI assistant effectively)

---

## 🔧 Troubleshooting

### Script Won't Run
```bash
# Make executable
chmod +x .copilot/scripts/load_context.sh
```

### VSCode Not Opening Docs
```bash
# Install VSCode CLI
# In VSCode: Cmd+Shift+P → "Shell Command: Install 'code' command in PATH"

# Or manually open:
code docs/context/PROJECT_REFERENCE_OVERVIEW.md
```

### Too Much Context
```bash
# Just load the 4 master docs
code docs/context/*.md

# Or open specific doc
code docs/QA_STRATEGY.md
```

### AI Seems Confused
- Make sure you loaded context first
- Use a conversation template
- Reference specific doc sections in your prompts
- Example: "According to SYSTEM_ARCHITECTURE_SUMMARY.md, the RAG pipeline has 7 nodes..."

---

## 🎓 Pro Tips

### Tip 1: Always Load Context First
Don't start conversations with AI without context. Run the load script first.

### Tip 2: Use Templates for Consistency
Templates ensure you provide complete context and get complete answers.

### Tip 3: Reference Specific Docs
Say "According to QA_STRATEGY.md..." instead of "I think..." - AI follows documented patterns.

### Tip 4: Keep CONTINUE_HERE.md Updated
After completing work, update this doc so next session starts fresh.

### Tip 5: Verify Context is Current
Check "Last Updated" dates. If > 30 days, verify info is still accurate.

---

## 🔗 Key Links

| Link | Purpose |
|------|---------|
| [`.copilot/README.md`](README.md) | Full documentation for this folder |
| [`.copilot/REQUIRED_READING.md`](REQUIRED_READING.md) | Master manifest (machine-readable) |
| [`CONTINUE_HERE.md`](../CONTINUE_HERE.md) | Current project status |
| [`docs/QA_STRATEGY.md`](../docs/QA_STRATEGY.md) | Testing & design principles |
| [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) | Coding conventions |

---

## 📞 Need Help?

1. Check `.copilot/README.md` for detailed explanations
2. Review `CONTINUE_HERE.md` for current status
3. Ask in team chat or GitHub issues

---

**Remember**: The 4 master docs are your source of truth. Read them first! 📚
