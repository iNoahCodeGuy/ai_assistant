# Quality Assurance Strategy

**Purpose**: Ensure conversation quality, code quality, and **documentation-code alignment** remain intact as the codebase evolves.

**Last Updated**: October 16, 2025

---

## Table of Contents
1. [Current Quality Standards](#current-quality-standards)
2. [Automated Testing](#automated-testing)
3. [**NEW: Documentation Alignment Testing**](#documentation-alignment-testing)
4. [**NEW: Feature Development Documentation Workflow**](#feature-development-documentation-workflow)
5. [Pre-Commit Hooks](#pre-commit-hooks)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Documentation Quality Standards](#documentation-quality-standards)
8. [Quarterly Documentation Audit](#quarterly-documentation-audit)

---

## Current Quality Standards

### 1. Conversation Quality (15 Tests)
**File**: `tests/test_conversation_quality.py`

| Standard | Test | Status |
|----------|------|--------|
| KB aggregated (not 245 rows) | `test_kb_coverage_aggregated_not_detailed` | ✅ |
| KPIs calculated | `test_kpi_metrics_calculated` | ✅ |
| Recent activity limited | `test_recent_activity_limited` | ✅ |
| Confessions private | `test_confessions_privacy_protected` | ✅ |
| Single follow-up prompt | `test_no_duplicate_prompts_in_full_flow` | ✅ |
| No emoji headers | `test_no_emoji_headers` | ✅ |
| LLM no self-prompts | `test_llm_no_self_generated_prompts` | ✅ |
| Code display graceful | `test_empty_code_index_shows_helpful_message` | ✅ |
| Code validation logic | `test_code_content_validation_logic` | ✅ |
| No information overload | `test_no_information_overload` | ✅ |
| Consistent formatting | `test_consistent_formatting_across_roles` | ✅ |
| No section iteration | `test_analytics_no_section_iteration` | ✅ |
| Prompts deprecated | `test_response_generator_no_prompts` | ✅ |
| Single prompt location | `test_conversation_nodes_single_prompt_location` | ✅ |
| **Q&A synthesis** | `test_no_qa_verbatim_responses`, `test_response_synthesis_in_prompts` | ✅ |

**Run**: `pytest tests/test_conversation_quality.py -v`

---

## **NEW: Documentation Alignment Testing**

### The Problem We're Solving

**Before**: Documentation could claim function names or flows that didn't match reality. Example:
- Docs said: `classify_intent` → Code actually used: `classify_query`
- Result: Developers waste time searching for functions that don't exist

**Solution**: Automated tests that verify documentation matches code.

---

### Test Suite: Documentation Alignment

**File**: `tests/test_documentation_alignment.py` (NEW)

#### Test 1: Conversation Pipeline Flow Matches Code
```python
def test_conversation_flow_documented_correctly():
    """Verify SYSTEM_ARCHITECTURE_SUMMARY describes actual pipeline."""
    
    # Read master documentation
    with open("docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md") as f:
        doc_content = f.read()
    
    # Extract documented node names from code section
    import re
    code_section = re.search(r"```python\n# Pipeline.*?\n(.*?)```", doc_content, re.DOTALL)
    if not code_section:
        pytest.fail("No code pipeline found in SYSTEM_ARCHITECTURE_SUMMARY.md")
    
    documented_nodes = []
    for line in code_section.group(1).split('\n'):
        if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('→'):
            # Extract node name (first word before whitespace or →)
            node = line.strip().split()[0].split('→')[0]
            if node and not node.startswith('Source:'):
                documented_nodes.append(node)
    
    # Get actual pipeline from code
    from src.flows.conversation_flow import run_conversation_flow
    import inspect
    source = inspect.getsource(run_conversation_flow)
    
    # Verify documented nodes appear in actual code
    actual_nodes = [
        "handle_greeting", "classify_query", "retrieve_chunks", 
        "generate_answer", "plan_actions", "apply_role_context", 
        "execute_actions", "log_and_notify"
    ]
    
    for node in actual_nodes:
        assert node in documented_nodes, (
            f"Node '{node}' exists in code but not documented in "
            f"SYSTEM_ARCHITECTURE_SUMMARY.md. Update docs to match implementation."
        )
    
    # Verify documented nodes actually exist in code
    for node in documented_nodes:
        if node in actual_nodes:  # Skip conceptual descriptions
            assert node in source, (
                f"Node '{node}' documented but doesn't exist in conversation_flow.py. "
                f"Remove from docs or implement in code."
            )
```

**What it catches**: Function name mismatches, missing nodes, phantom nodes

---

#### Test 2: Code References Are Valid File Paths
```python
def test_documentation_file_references_valid():
    """Ensure all file paths mentioned in docs actually exist."""
    import os
    import re
    
    doc_files = [
        "docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md",
        "docs/context/DATA_COLLECTION_AND_SCHEMA_REFERENCE.md",
        "docs/RAG_ENGINE.md",
        "docs/CONVERSATION_PIPELINE_MODULES.md",
    ]
    
    invalid_references = []
    
    for doc_file in doc_files:
        with open(doc_file) as f:
            content = f.read()
        
        # Find references like "src/flows/core_nodes.py" or "Source: src/..."
        file_refs = re.findall(r'(?:src/[\w/]+\.py)|(?:tests/[\w/]+\.py)', content)
        
        for ref in file_refs:
            if not os.path.exists(ref):
                invalid_references.append({
                    "doc": doc_file,
                    "reference": ref,
                    "line": content[:content.find(ref)].count('\n') + 1
                })
    
    assert len(invalid_references) == 0, (
        f"Found {len(invalid_references)} invalid file references:\\n" +
        "\\n".join([
            f"  {inv['doc']} line {inv['line']}: {inv['reference']}"
            for inv in invalid_references
        ]) +
        "\\nUpdate documentation to reference correct files."
    )
```

**What it catches**: Outdated file paths, typos, files that were moved/deleted

---

#### Test 3: Role Names Match Between Docs and Code
```python
def test_role_names_consistent():
    """Verify role names in docs match actual role definitions."""
    
    # Get documented roles from PROJECT_REFERENCE_OVERVIEW
    with open("docs/context/PROJECT_REFERENCE_OVERVIEW.md") as f:
        doc_content = f.read()
    
    doc_roles = set()
    if "Software Developer" in doc_content:
        doc_roles.add("Software Developer")
    if "Hiring Manager (technical)" in doc_content:
        doc_roles.add("Hiring Manager (technical)")
    if "Hiring Manager (nontechnical)" in doc_content or "Hiring Manager (non-technical)" in doc_content:
        doc_roles.add("Hiring Manager (nontechnical)")
    if "Just Exploring" in doc_content or "Just looking" in doc_content:
        doc_roles.add("Just looking around")
    if "Confess" in doc_content:
        doc_roles.add("Looking to confess crush")
    
    # Get actual roles from code
    from src.agents.roles import AVAILABLE_ROLES
    code_roles = set(AVAILABLE_ROLES)
    
    # Check for mismatches
    missing_in_docs = code_roles - doc_roles
    extra_in_docs = doc_roles - code_roles
    
    assert len(missing_in_docs) == 0, (
        f"Roles in code but not documented: {missing_in_docs}. "
        f"Add to docs/context/PROJECT_REFERENCE_OVERVIEW.md"
    )
    
    assert len(extra_in_docs) == 0, (
        f"Roles documented but not in code: {extra_in_docs}. "
        f"Remove from docs or implement in src/agents/roles.py"
    )
```

**What it catches**: New roles added without documentation, renamed roles, deprecated roles still in docs

---

#### Test 4: Temperature Settings Match Documentation
```python
def test_temperature_settings_documented_correctly():
    """Verify temperature value in docs matches actual code."""
    
    # Get documented temperature
    with open("docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md") as f:
        doc_content = f.read()
    
    import re
    temp_match = re.search(r'temperature[:\s]+(\d+\.?\d*)', doc_content)
    if not temp_match:
        pytest.fail("Temperature setting not documented in SYSTEM_ARCHITECTURE_SUMMARY.md")
    
    documented_temp = float(temp_match.group(1))
    
    # Get actual temperature from code
    from src.core.rag_factory import RagFactory
    import inspect
    source = inspect.getsource(RagFactory.create_llm)
    
    code_temp_match = re.search(r'temperature=(\d+\.?\d*)', source)
    assert code_temp_match, "Temperature not found in RagFactory.create_llm"
    
    actual_temp = float(code_temp_match.group(1))
    
    assert documented_temp == actual_temp, (
        f"Temperature mismatch: docs say {documented_temp}, code uses {actual_temp}. "
        f"Update docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md to match code."
    )
```

**What it catches**: Outdated configuration values in documentation

---

#### Test 5: Master Docs Cross-Reference Integrity
```python
def test_master_docs_cross_references_valid():
    """Ensure cross-references between master docs point to existing sections."""
    
    import os
    import re
    
    master_docs = {
        "PROJECT_REFERENCE_OVERVIEW.md": None,
        "SYSTEM_ARCHITECTURE_SUMMARY.md": None,
        "DATA_COLLECTION_AND_SCHEMA_REFERENCE.md": None,
        "CONVERSATION_PERSONALITY.md": None,
    }
    
    # Read all master docs and extract headers
    for doc_name in master_docs:
        path = f"docs/context/{doc_name}"
        with open(path) as f:
            content = f.read()
            # Extract all markdown headers
            headers = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
            master_docs[doc_name] = {
                "content": content,
                "headers": headers,
                "path": path
            }
    
    # Find cross-references (See FILENAME.md, reference to FILENAME, etc.)
    invalid_refs = []
    for doc_name, doc_data in master_docs.items():
        # Find references to other master docs
        for other_doc in master_docs:
            if other_doc != doc_name and other_doc in doc_data["content"]:
                # Valid reference, but check if it points to existing content
                pass
    
    # Check for references to sections that don't exist
    # Example: "See CONVERSATION_PERSONALITY.md section X" where X doesn't exist
    
    assert len(invalid_refs) == 0, (
        f"Found {len(invalid_refs)} broken cross-references in master docs"
    )
```

**What it catches**: Broken links between master documentation files

---

### Running Documentation Alignment Tests

```bash
# Run all documentation alignment tests
pytest tests/test_documentation_alignment.py -v

# Run specific test
pytest tests/test_documentation_alignment.py::test_conversation_flow_documented_correctly -v

# Run with detailed output
pytest tests/test_documentation_alignment.py -vv
```

---

## **Feature Development Documentation Workflow**

### When Adding New Features or Changing Behavior

This section answers: **"Should I create a new .md file or update an existing one?"**

---

### Decision Tree: Where to Document Changes

```
┌─ Is this a NEW feature (adds capability)?
│  ├─ YES → Create feature doc in docs/features/
│  │         Example: DISPLAY_INTELLIGENCE_IMPLEMENTATION.md
│  │
│  └─ NO (existing feature change)
│      └─ Is this an IMPLEMENTATION detail change?
│          ├─ YES (e.g., refactored code, new helper function)
│          │  └─ Update existing feature doc in docs/features/
│          │
│          └─ NO (BEHAVIOR or ARCHITECTURE change)
│              └─ Update MASTER docs in docs/context/
│                  - SYSTEM_ARCHITECTURE_SUMMARY.md
│                  - PROJECT_REFERENCE_OVERVIEW.md
│                  - DATA_COLLECTION_AND_SCHEMA_REFERENCE.md
│                  - CONVERSATION_PERSONALITY.md
```

---

### Feature Documentation Checklist

#### ✅ **Scenario 1: Adding a New Feature**

**Example**: Adding sentiment analysis to user queries

**Required Documentation**:
1. **Create new feature doc**: `docs/features/SENTIMENT_ANALYSIS_IMPLEMENTATION.md`
   - Include: Problem statement, implementation approach, code files, examples
   - Template available in `docs/features/README.md`

2. **Update CHANGELOG.md**:
   ```markdown
   ## [Unreleased]
   ### Added
   - Sentiment analysis for query classification
   ```

3. **Update master docs IF behavior changes**:
   - `SYSTEM_ARCHITECTURE_SUMMARY.md`: Add sentiment node to pipeline
   - `PROJECT_REFERENCE_OVERVIEW.md`: Mention sentiment capability
   - `CONVERSATION_PERSONALITY.md`: IF sentiment affects tone

4. **Add tests**:
   - Conversation quality test (if user-facing)
   - Alignment test (if documented functions/flow)

**Files Created/Modified**:
```
✅ NEW: docs/features/SENTIMENT_ANALYSIS_IMPLEMENTATION.md
✅ MODIFIED: CHANGELOG.md
✅ MODIFIED: docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md (if pipeline changes)
✅ NEW: tests/test_sentiment_analysis.py
```

---

#### ✅ **Scenario 2: Changing Existing Feature Implementation**

**Example**: Refactoring code display logic without changing behavior

**Required Documentation**:
1. **Update existing feature doc**: `docs/features/DISPLAY_INTELLIGENCE_IMPLEMENTATION.md`
   - Update code file references
   - Add "Refactoring Notes" section if architecture changed
   - Keep behavior description unchanged

2. **Update CHANGELOG.md**:
   ```markdown
   ## [Unreleased]
   ### Changed
   - Refactored code display logic for maintainability
   ```

3. **Master docs**: NO update needed (behavior unchanged)

4. **Run alignment tests**: Ensure function references still valid

**Files Modified**:
```
✅ MODIFIED: docs/features/DISPLAY_INTELLIGENCE_IMPLEMENTATION.md
✅ MODIFIED: CHANGELOG.md
✅ RUN: pytest tests/test_documentation_alignment.py -v
```

---

#### ✅ **Scenario 3: Changing System Behavior/Architecture**

**Example**: Changing conversation pipeline from 8 nodes to 10 nodes

**Required Documentation**:
1. **Update MASTER doc**: `docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md`
   - Update pipeline diagram
   - Update function list with source file references
   - Explain why architecture changed

2. **Update related feature docs** (if affected):
   - Example: If greeting node split into two, update greeting implementation doc

3. **Update CHANGELOG.md**:
   ```markdown
   ## [Unreleased]
   ### Changed
   - Conversation pipeline: Split greeting logic into separate validation and response nodes
   ```

4. **Update alignment tests**:
   ```python
   # In test_documentation_alignment.py
   actual_nodes = [
       "handle_greeting", "validate_greeting", "respond_greeting",  # ← Added new node
       "classify_query", "retrieve_chunks", ...
   ]
   ```

**Files Modified**:
```
✅ MODIFIED: docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md
✅ MODIFIED: docs/features/GREETING_INTELLIGENCE.md (example)
✅ MODIFIED: CHANGELOG.md
✅ MODIFIED: tests/test_documentation_alignment.py
✅ RUN: pytest tests/ -v
```

---

#### ✅ **Scenario 4: Adding New Role or Query Type**

**Example**: Adding "Recruiter" role with specialized retrieval

**Required Documentation**:
1. **Update MASTER docs**:
   - `PROJECT_REFERENCE_OVERVIEW.md`: Add role to list with description
   - `SYSTEM_ARCHITECTURE_SUMMARY.md`: Explain retrieval strategy
   - `CONVERSATION_PERSONALITY.md`: Define tone/enthusiasm level

2. **Create role-specific doc** (optional, if complex):
   - `docs/features/RECRUITER_ROLE_IMPLEMENTATION.md`

3. **Update CHANGELOG.md**:
   ```markdown
   ## [Unreleased]
   ### Added
   - Recruiter role with specialized hiring pipeline knowledge
   ```

4. **Add alignment tests**:
   ```python
   # In test_documentation_alignment.py
   EXPECTED_ROLES = [
       "hiring_manager_nontechnical",
       "hiring_manager_technical",
       "software_developer",
       "just_looking_around",
       "looking_to_confess_crush",
       "recruiter",  # ← New role
   ]
   ```

**Files Modified**:
```
✅ MODIFIED: docs/context/PROJECT_REFERENCE_OVERVIEW.md
✅ MODIFIED: docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md
✅ MODIFIED: docs/context/CONVERSATION_PERSONALITY.md
✅ MODIFIED: CHANGELOG.md
✅ MODIFIED: tests/test_documentation_alignment.py
✅ OPTIONAL: docs/features/RECRUITER_ROLE_IMPLEMENTATION.md
```

---

### Quick Reference: Documentation Types

| Documentation Type | Purpose | When to Use | Location |
|-------------------|---------|-------------|----------|
| **Master Docs** | Define system behavior, architecture, personality | Behavior/architecture changes | `docs/context/` |
| **Feature Docs** | Implementation details, code walkthrough | New features, refactors | `docs/features/` |
| **Setup Guides** | Installation, configuration, deployment | Adding new services | `docs/setup/` |
| **Analysis Docs** | Technical decisions, performance analysis | Major architectural decisions | `docs/analysis/` |
| **Implementation Reports** | Completion summaries for large changes | End of feature development cycle | `docs/implementation/` |
| **CHANGELOG** | User-facing changes | Every code change | Root: `CHANGELOG.md` |

---

### Documentation Anti-Patterns (Don't Do This)

❌ **Wrong: Creating duplicate behavior documentation**
```markdown
# docs/features/MY_FEATURE.md
The system uses a temperature of 0.4 for LLM calls...
```
→ This duplicates `SYSTEM_ARCHITECTURE_SUMMARY.md`

✅ **Right: Reference master docs**
```markdown
# docs/features/MY_FEATURE.md
This feature uses the standard LLM configuration (see 
[SYSTEM_ARCHITECTURE_SUMMARY](../context/SYSTEM_ARCHITECTURE_SUMMARY.md#llm-configuration))...
```

---

❌ **Wrong: Using conceptual names**
```markdown
The classify_intent function determines query type...
```
→ Function doesn't exist with that name

✅ **Right: Use actual code names**
```markdown
The `classify_query` function (in `src/flows/conversation_nodes.py`, line 45) 
determines query type...
```

---

❌ **Wrong: Documenting without testing**
```markdown
# Add new feature documentation
# No alignment test created
```
→ Documentation will drift from code

✅ **Right: Add alignment test**
```python
# tests/test_documentation_alignment.py
def test_my_new_feature_documented():
    """Verify my_feature function appears in feature docs."""
    with open("docs/features/MY_FEATURE.md") as f:
        assert "my_feature_function" in f.read()
```

---

### Pull Request Checklist for Feature Changes

```markdown
## Documentation Updates (Required)
- [ ] CHANGELOG.md updated with user-facing changes
- [ ] Master docs updated (if behavior/architecture changed)
- [ ] Feature doc created/updated (implementation details)
- [ ] Alignment test added (if new documented functions/flow)
- [ ] All tests passing: `pytest tests/ -v`

## Documentation Type Decision
- [ ] I understand when to create new docs vs update existing
- [ ] I used actual function/file names (not conceptual terms)
- [ ] I cross-referenced master docs (not duplicated content)
- [ ] I added code file references with line numbers
```

---

## Pre-Commit Hooks

**File**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      # Conversation quality checks
      - id: no-emoji-headers
        name: No emoji in section headers
        entry: python -c "import sys, re; sys.exit(1 if re.search(r'^###?\s+[🎯📊🚀💡]', open(sys.argv[1]).read(), re.M) else 0)"
        language: system
        files: \\.py$
      
      # Documentation alignment checks (NEW)
      - id: doc-file-references
        name: Documentation file references valid
        entry: pytest tests/test_documentation_alignment.py::test_documentation_file_references_valid -v
        language: system
        files: docs/.*\\.md$
        pass_filenames: false
      
      - id: doc-role-consistency
        name: Role names match docs and code
        entry: pytest tests/test_documentation_alignment.py::test_role_names_consistent -v
        language: system
        files: (docs/context/PROJECT_REFERENCE_OVERVIEW\\.md|src/agents/roles\\.py)
        pass_filenames: false
```

**Install**: `pre-commit install`

---

## CI/CD Pipeline

**File**: `.github/workflows/quality-gates.yml`

```yaml
name: Quality Gates

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  conversation-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run conversation quality tests
        run: pytest tests/test_conversation_quality.py -v
  
  documentation-alignment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run documentation alignment tests
        run: pytest tests/test_documentation_alignment.py -v
      - name: Verify all doc file references valid
        run: |
          # Additional check: grep for broken markdown links
          find docs -name "*.md" -exec grep -H "\[.*\](.*)" {} \\; | \
          grep -v "http" | grep -v "^.*:.*(.*\.md)" || true
```

---

## Documentation Quality Standards

### 1. Single Source of Truth (SSOT) Principle

**Rule**: Master documentation in `docs/context/` is authoritative. All other docs MUST:
- Cross-reference master docs, never duplicate
- Describe implementation details ("how we built it"), not behavior ("what it does")
- Use actual function/file names from code, not conceptual terms

**Example - ❌ Wrong**:
```markdown
# Some Feature Doc
The system uses classify_intent to understand user queries.
```

**Example - ✅ Right**:
```markdown
# Some Feature Doc
The system uses `classify_query()` (see src/flows/query_classification.py) 
to understand user intent, as described in docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md.
```

---

### 2. Code-First Documentation Updates

**Rule**: When code changes, documentation MUST be updated in the same commit.

**Process**:
1. Developer changes function name: `classify_intent` → `classify_query`
2. Same commit updates:
   - Master docs: `docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md`
   - Implementation docs: Any doc that references the function
   - Tests: Update `test_conversation_flow_documented_correctly()`
3. CI fails if docs not updated (caught by alignment tests)

---

### 3. Documentation Hygiene Checklist

**Before adding new documentation**, verify:

- [ ] Can this information be added to existing doc instead of creating new file?
- [ ] Does this doc cross-reference master docs for behavior/concepts?
- [ ] Have I used actual function names (not conceptual placeholders)?
- [ ] Have I included file paths to referenced code?
- [ ] Have I added this doc to the README structure guide?
- [ ] If creating feature doc, does CHANGELOG.md reference it?

**Before updating existing documentation**:

- [ ] Am I updating master docs? (Requires extra review - these are source of truth)
- [ ] Do code references still point to correct files/lines?
- [ ] Do cross-references to other docs still work?
- [ ] Have I tested that code examples still run?

---

### 4. Master Documentation Update Process

**Special care for `docs/context/` files** (these guide Copilot and developers):

1. **Propose change**: Create issue explaining what's outdated and why
2. **Review actual code**: Verify current implementation before documenting
3. **Update master doc**: Use actual function names, file paths, current behavior
4. **Update alignment tests**: If structure changed, update test expectations
5. **PR review**: Requires 2 approvals for master doc changes
6. **Copilot verification**: Test that Copilot references updated content correctly

---

## Quarterly Documentation Audit

**Schedule**: Every 3 months (January, April, July, October)

**Checklist**:

### 1. Run Full Alignment Test Suite
```bash
pytest tests/test_documentation_alignment.py -v
```
Fix any failures before proceeding.

### 2. Manual Cross-Check
- [ ] Open `docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md`
- [ ] For each function mentioned, CMD+click to verify it exists in codebase
- [ ] For each file path, verify file still exists at that location
- [ ] For each configuration value (temperature, model, etc.), verify matches code

### 3. Master Docs Review
- [ ] PROJECT_REFERENCE_OVERVIEW: Do roles, stack, behavior match reality?
- [ ] SYSTEM_ARCHITECTURE_SUMMARY: Does conversation flow match code?
- [ ] DATA_COLLECTION_AND_SCHEMA_REFERENCE: Do tables, queries match Supabase?
- [ ] CONVERSATION_PERSONALITY: Do greetings match src/flows/greetings.py?

### 4. Feature Docs Review
- [ ] Check `docs/features/` for outdated implementation notes
- [ ] Archive docs for deprecated features to `docs/archive/`
- [ ] Update CHANGELOG.md with any undocumented changes

### 5. Code Reference Validation
```bash
# Find all file references in docs
grep -r "src/.*\.py" docs/ | while read line; do
  file=$(echo "$line" | grep -o "src/[^ ]*\.py")
  if [ ! -f "$file" ]; then
    echo "BROKEN REFERENCE: $line"
  fi
done
```

### 6. Redundancy Check
- [ ] Look for duplicate content (same concept explained in multiple docs)
- [ ] Consolidate or add cross-references
- [ ] Update DOCUMENTATION_CONSOLIDATION_ANALYSIS.md if structure changes

---

## Success Metrics

### Documentation Alignment Metrics

| Metric | Target | Current | How to Measure |
|--------|--------|---------|----------------|
| File reference validity | 100% | - | `test_documentation_file_references_valid` |
| Function name accuracy | 100% | - | `test_conversation_flow_documented_correctly` |
| Role name consistency | 100% | - | `test_role_names_consistent` |
| Config value accuracy | 100% | - | `test_temperature_settings_documented_correctly` |
| Quarterly audit completion | 4/year | 0 | Manual tracking |
| Doc alignment test coverage | 10+ tests | 5 | Count tests in `test_documentation_alignment.py` |

### Conversation Quality Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Automated tests passing | 100% | ✅ 15/15 |
| Manual test checklist items | 100% | TBD |
| User-reported quality issues | <2/month | Track in issues |

---

## Adding Documentation Alignment Tests

### When to Add New Test

Add documentation alignment test when:
1. **New feature added**: Test that feature is documented
2. **Architecture changes**: Test that master docs reflect new structure
3. **Bug from misalignment**: Add test that would have caught it

### Test Template

```python
def test_YOUR_ALIGNMENT_CHECK():
    """Verify [WHAT] matches between docs and code."""
    
    # 1. Read documentation
    with open("docs/PATH/TO/DOC.md") as f:
        doc_content = f.read()
    
    # 2. Extract expected value from docs
    import re
    expected = re.search(r'PATTERN', doc_content).group(1)
    
    # 3. Get actual value from code
    from src.module import function
    import inspect
    actual = inspect.getsource(function)
    
    # 4. Assert they match
    assert expected in actual, (
        f"Documentation says '{expected}' but code doesn't match. "
        f"Update docs/PATH/TO/DOC.md to reflect current implementation."
    )
```

---

## Preventing Future Misalignment

### 1. Editor Integration

**VS Code**: Add to `.vscode/settings.json`:
```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests",
    "--doctest-modules"
  ],
  "python.linting.enabled": true,
  "grammarly.files.include": ["**/*.md"],
  "grammarly.selectors": [
    {
      "language": "markdown",
      "scheme": "file"
    }
  ]
}
```

### 2. Pull Request Template

**File**: `.github/pull_request_template.md`

**See**: [Feature Development Documentation Workflow](#feature-development-documentation-workflow) for detailed guidance.

```markdown
## Changes Made
- [ ] Code changes described
- [ ] If changing function names/signatures: Updated docs
- [ ] If adding new feature: Added to CHANGELOG.md
- [ ] If modifying conversation flow: Updated SYSTEM_ARCHITECTURE_SUMMARY.md

## Documentation Updates (See QA_STRATEGY.md §4 for Workflow)
- [ ] Master docs updated (if behavior/architecture changed)
- [ ] Feature doc created/updated (implementation details)
- [ ] I understand when to create new docs vs update existing
- [ ] Code references use actual function/file names (not conceptual terms)
- [ ] Alignment test added (if new documented functions/flow)
- [ ] Tests pass: `pytest tests/test_documentation_alignment.py -v`

## Testing
- [ ] All conversation quality tests pass
- [ ] All documentation alignment tests pass
- [ ] Manual testing completed
```

### 3. Commit Message Convention

When updating docs, use these prefixes:
- `docs(master): Update SYSTEM_ARCHITECTURE_SUMMARY` - Master doc change
- `docs(feature): Update DISPLAY_INTELLIGENCE` - Feature doc change
- `docs(fix): Fix broken file reference in RAG_ENGINE.md` - Doc bug fix
- `docs(align): Update flow to match code refactor` - Alignment fix

---

## Related Documentation

- **Test Inventory**: See "Current Quality Standards" section above
- **Conversation Quality**: `tests/test_conversation_quality.py`
- **Documentation Consolidation**: `DOCUMENTATION_CONSOLIDATION_ANALYSIS.md`
- **Code Alignment Report**: `CODE_DOCUMENTATION_ALIGNMENT_REPORT.md`
- **Master Documentation**: `docs/context/` directory

---

**Last Review**: October 16, 2025 (Added Feature Development Documentation Workflow)  
**Next Review**: January 16, 2026  
**Owner**: Engineering Team
