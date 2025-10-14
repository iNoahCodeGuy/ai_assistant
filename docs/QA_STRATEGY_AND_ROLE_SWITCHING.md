# QA Strategy Display & Role-Switching Suggestions

## Overview

Enhanced conversation flow to showcase the automated quality assurance system and guide users to the most appropriate role for their questions.

## Features Added

### 1. QA Strategy Display ✅

**When**: Technical roles (Hiring Manager technical, Software Developer) ask "how does this product work?" or similar questions.

**What's Shown**:
```markdown
**Quality Assurance**
- **Automated Regression Tests**: 14 test cases cover analytics display, prompt deduplication, 
  professional formatting, and code validation (all passing in ~1.2s).
- **Pre-Commit Hooks**: Catch emoji headers, duplicate prompts, and raw data dumps before commit.
- **CI/CD Quality Gates**: GitHub Actions block merges if quality standards are violated.
- **Production Monitoring**: Daily checks track success rates, response times, and formatting compliance.
- **Documentation**: Comprehensive strategy (`docs/QUALITY_ASSURANCE_STRATEGY.md`) ensures team alignment.

This system prevents regression as the codebase grows—new features can't break conversation quality.
```

**Trigger Queries**:
- "how does this product work?"
- "what is this product?"
- "how does this work?"
- "what does this do?"
- "explain this product"
- "how is this built?"
- "tell me about this"
- Any query with "product" + "how/what/explain/work"

### 2. Role-Switching Suggestions ✅

**When**: Nontechnical Hiring Manager asks technical questions.

**What's Shown**:
```markdown
💡 **Tip**: For more detailed technical insights, try switching to the **Hiring Manager (technical)** role. 
That role provides code snippets, architecture diagrams, and implementation details.
```

**Triggers**:
- Query classified as "technical" type
- Code display requested ("show me the code")
- Import explanation requested ("why use supabase?")
- Product architecture questions

## Implementation Details

### Content Blocks (`src/flows/content_blocks.py`)

**New Functions**:

```python
def qa_strategy_block() -> str:
    """Generate QA strategy overview for product/architecture questions."""
    # Returns 6-bullet overview of automated quality system
    
def role_switch_suggestion(target_role: str) -> str:
    """Generate suggestion to switch roles for better answers."""
    # Returns formatted tip with role name
```

### Conversation Nodes (`src/flows/conversation_nodes.py`)

**Updated Functions**:

1. **`plan_actions()`** - Lines 177-235
   - Detects product questions via pattern matching
   - Adds `include_qa_strategy` action for technical roles
   - Adds `suggest_technical_role_switch` action for nontechnical roles
   - Triggers on code/import/architecture questions

2. **`apply_role_context()`** - Lines 305-311
   - Renders QA strategy block when action present
   - Renders role-switch suggestion when action present

## Example Conversations

### Scenario 1: Technical Role Asks About Product

**Role**: Hiring Manager (technical)  
**Query**: "how does this product work?"

**Actions Triggered**:
- `include_qa_strategy` ✅
- `include_purpose_overview` ✅
- `include_architecture_overview` ✅
- `summarize_data_strategy` ✅
- `provide_data_tables` ✅
- `explain_enterprise_usage` ✅
- `explain_stack_currency` ✅
- `highlight_enterprise_adaptability` ✅
- `include_code_snippets` ✅

**Response Includes**: QA strategy block + full technical deep-dive

---

### Scenario 2: Nontechnical Role Asks About Product

**Role**: Hiring Manager (nontechnical)  
**Query**: "how does this product work?"

**Actions Triggered**:
- `suggest_technical_role_switch` ✅

**Response Includes**: Basic explanation + suggestion to switch to technical role

---

### Scenario 3: Nontechnical Role Asks for Code

**Role**: Hiring Manager (nontechnical)  
**Query**: "show me the code for the retrieval system"

**Actions Triggered**:
- `suggest_technical_role_switch` ✅

**Response Includes**: High-level explanation + role-switching tip

---

### Scenario 4: Nontechnical Role Asks About Stack

**Role**: Hiring Manager (nontechnical)  
**Query**: "why did you use supabase?"

**Actions Triggered**:
- `explain_imports` ✅
- `suggest_technical_role_switch` ✅

**Response Includes**: Import explanation + role-switching tip

## Benefits

### For Technical Evaluators
- **Transparency**: Shows Noah understands quality engineering
- **Credibility**: Demonstrates systematic approach to preventing bugs
- **Depth**: Provides concrete metrics (14 tests, 1.2s runtime, CI/CD gates)

### For Nontechnical Users
- **Guidance**: Clear path to getting more detailed answers
- **User Experience**: Doesn't overwhelm with technical details they didn't ask for
- **Empowerment**: Teaches them how to get better answers

### For System Maintainability
- **Modularity**: QA content in separate reusable block
- **Testability**: All 14 quality tests still passing
- **Extensibility**: Easy to add more role-switching triggers

## Testing

### Unit Tests Passing ✅
```bash
pytest tests/test_conversation_quality.py -v
# 14 passed in 1.07s
```

### Manual Testing ✅
All scenarios verified:
- ✅ Technical role + product question → QA strategy shown
- ✅ Nontechnical role + product question → Role-switch suggestion shown
- ✅ Nontechnical role + code request → Role-switch suggestion shown
- ✅ Nontechnical role + stack question → Both import explanation + suggestion

## Next Steps (Optional Enhancements)

### Phase 1: Expand Triggers
- Add QA strategy to "show me analytics" responses
- Show QA strategy in data_reporting.py full reports
- Include QA strategy in architecture overviews

### Phase 2: Interactive Role Switching
- Add button in Streamlit UI for one-click role switch
- Preserve conversation history when switching roles
- Log role-switch actions for analytics

### Phase 3: Role Recommendations
- Analyze conversation patterns
- Proactively suggest role changes based on question trajectory
- "You've asked 3 technical questions—want to switch to technical role?"

## Commit History

```
b817874 - feat: Add QA strategy to product explanations and role-switching suggestions
4d3a3ed - docs: Add quality assurance implementation summary
592b906 - feat: Add comprehensive quality assurance strategy with automated tests
```

## Related Documentation

- **QA Strategy**: `docs/QUALITY_ASSURANCE_STRATEGY.md`
- **QA Implementation**: `docs/QA_IMPLEMENTATION_SUMMARY.md`
- **Quality Tests**: `tests/test_conversation_quality.py`
- **Content Blocks**: `src/flows/content_blocks.py`
- **Conversation Nodes**: `src/flows/conversation_nodes.py`
