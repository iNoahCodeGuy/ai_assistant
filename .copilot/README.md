# 🤖 AI Copilot Context Automation

**Purpose**: Automate context loading for GitHub Copilot and other AI assistants during development.

**Created**: October 19, 2025
**Last Updated**: October 19, 2025

---

## 📁 Folder Structure

```
.copilot/
├── README.md                    # This file
├── REQUIRED_READING.md          # Master document manifest (machine-readable)
├── QUICK_START.md               # Developer quick reference
├── templates/
│   ├── implement_feature.md     # Template for new features
│   ├── fix_tests.md             # Template for debugging tests
│   ├── deploy_production.md    # Template for deployment
│   ├── architecture_decision.md # Template for arch decisions
│   └── code_review.md           # Template for PR reviews
└── scripts/
    ├── load_context.sh          # Shell script to open relevant docs
    └── verify_context.py        # Python script to verify docs exist
```

---

## 🚀 Quick Start

### For New Features
```bash
# Load feature development context
./.copilot/scripts/load_context.sh feature

# Use template
cat .copilot/templates/implement_feature.md
# Copy template into AI chat, fill in [FEATURE_NAME]
```

### For Fixing Tests
```bash
# Load testing context
./.copilot/scripts/load_context.sh test

# Use template
cat .copilot/templates/fix_tests.md
```

### For Deployment
```bash
# Load deployment context
./.copilot/scripts/load_context.sh deploy

# Use template
cat .copilot/templates/deploy_production.md
```

### For Architecture Decisions
```bash
# Load architecture context
./.copilot/scripts/load_context.sh architecture

# Use template
cat .copilot/templates/architecture_decision.md
```

---

## 📚 Context Tiers

### Tier 1: Always Load (Master Docs)
- `docs/context/PROJECT_REFERENCE_OVERVIEW.md`
- `docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md`
- `docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md`
- `docs/context/CONVERSATION_PERSONALITY.md`

### Tier 2: Daily Reference (Development)
- `CONTINUE_HERE.md` (current status)
- `docs/QA_STRATEGY.md` (testing standards)
- `.github/copilot-instructions.md` (conventions)
- `docs/LANGGRAPH_ALIGNMENT.md` (architecture decisions)

### Tier 3: Feature-Specific (On-Demand)
- `docs/ROLE_FEATURES.md`
- `docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md`
- `docs/RAG_ENGINE.md`
- `docs/EXTERNAL_SERVICES.md`

### Tier 4: Reference Only (Optional)
- `README.md`
- `CHANGELOG.md`
- `docs/features/ANALYTICS_IMPLEMENTATION.md`

---

## 🔧 Usage Examples

### Example 1: Starting Work on Resume Feature

```bash
# 1. Load context
./.copilot/scripts/load_context.sh feature

# 2. Get template
cat .copilot/templates/implement_feature.md > /tmp/prompt.md

# 3. Edit template (replace placeholders)
# [FEATURE_NAME] → "Resume Download Button"
# [RELATED_FEATURE] → "INTELLIGENT_RESUME_DISTRIBUTION"

# 4. Use in AI chat
cat /tmp/prompt.md
# Copy/paste into GitHub Copilot Chat
```

### Example 2: Debugging Failing Tests

```bash
# 1. Load context
./.copilot/scripts/load_context.sh test

# 2. Run tests to see failures
pytest tests/test_error_handling.py -v

# 3. Get debugging template
cat .copilot/templates/fix_tests.md

# 4. Fill in [TEST_FILE] with actual file
# 5. Paste into AI chat with test output
```

### Example 3: Pre-Deployment Checklist

```bash
# 1. Load deployment context
./.copilot/scripts/load_context.sh deploy

# 2. Get deployment template
cat .copilot/templates/deploy_production.md

# 3. Work through checklist with AI
# - Verify tests passing
# - Check environment variables
# - Review monitoring setup
```

---

## 📖 Key Files Explained

### REQUIRED_READING.md
- Machine-readable manifest of all documentation
- Priority levels (CRITICAL, HIGH, MEDIUM, LOW)
- Auto-load triggers by task type
- **Use**: Reference to understand what docs exist and when to load them

### templates/*.md
- Pre-written conversation starters for AI assistants
- Include required context, expected outputs, and checklists
- **Use**: Copy/paste into AI chat, fill in placeholders

### scripts/load_context.sh
- Shell script to open relevant documents in VSCode
- Modes: feature, test, deploy, architecture, role, default
- **Use**: Run before starting work on a specific task type

### scripts/verify_context.py
- Python script to verify all referenced docs exist
- Checks for broken links and missing files
- **Use**: Run periodically to ensure docs are up-to-date

---

## 🎯 Best Practices

### When Starting a New Task
1. Load context first: `./.copilot/scripts/load_context.sh [mode]`
2. Get template: `cat .copilot/templates/[template].md`
3. Review master docs (Tier 1)
4. Use AI assistant with full context

### When Context Feels Incomplete
1. Check `REQUIRED_READING.md` for related docs
2. Load additional docs manually
3. Update templates if needed

### When Documentation Changes
1. Update `REQUIRED_READING.md` manifest
2. Run `./.copilot/scripts/verify_context.py`
3. Fix any broken references

### When Onboarding New Developers
1. Share this README
2. Run: `./.copilot/scripts/load_context.sh default`
3. Review Tier 1 docs together
4. Practice using templates

---

## 🔄 Maintenance

### Weekly
- Run `verify_context.py` to check for broken links
- Update `REQUIRED_READING.md` if new docs added

### Monthly
- Review templates for accuracy
- Update priority levels based on usage
- Archive outdated templates

### Per Feature
- Update relevant templates with lessons learned
- Add new templates if new patterns emerge

---

## 🆘 Troubleshooting

### "Context script not found"
```bash
# Make script executable
chmod +x .copilot/scripts/load_context.sh
```

### "Documents not opening in VSCode"
```bash
# Check if 'code' command is installed
which code

# If not, install VSCode CLI:
# VSCode → Cmd+Shift+P → "Shell Command: Install 'code' command in PATH"
```

### "Too much context, AI confused"
- Use more specific mode: `./load_context.sh test` instead of `default`
- Load Tier 1 only: `code docs/context/*.md`
- Reference one template at a time

### "Template outdated"
- Check `CONTINUE_HERE.md` for current project status
- Update template with current file paths
- Submit PR with updated template

---

## 🤝 Contributing

### Adding New Templates
1. Create `.copilot/templates/[new_template].md`
2. Follow existing template format
3. Update this README with usage example
4. Add to `REQUIRED_READING.md` if referencing new docs

### Improving Scripts
1. Test changes locally first
2. Ensure backward compatibility
3. Update script comments
4. Document new modes/options in this README

### Updating Documentation Manifest
1. Edit `REQUIRED_READING.md`
2. Run `verify_context.py` to validate
3. Update priority levels if needed
4. Commit changes

---

## 📞 Support

For questions or issues:
1. Check `CONTINUE_HERE.md` for current project status
2. Review `.github/copilot-instructions.md` for conventions
3. Ask in team chat or open GitHub issue

---

**Happy coding with AI assistance! 🚀**
