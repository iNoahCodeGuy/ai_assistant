# Node Migration Guide: Dataclass → TypedDict

**Date:** October 17, 2025
**Status:** ✅ POC Complete - Pattern Validated
**POC Node:** `classify_query` (20/20 tests passing)

---

## Purpose

This guide documents the proven migration pattern for converting conversation nodes from the old `@dataclass` pattern to LangGraph-compatible TypedDict pattern.

**Reference Implementation:** [Tech With Tim LangGraph Tutorial](https://github.com/techwithtim/LangGraph-Tutorial) - See `main.py` lines 15-42 for node signature patterns

---

## Migration Pattern (Proven with `classify_query`)

### Before (Old Dataclass Pattern)

```python
from src.state.conversation_state import ConversationState  # OLD dataclass

def classify_query(state: ConversationState) -> ConversationState:
    """Old pattern: Mutates dataclass, returns modified instance."""

    # Direct mutation
    lowered = state.query.lower()

    if "technical" in lowered:
        state.stash("query_type", "technical")  # Mutates state.extras dict

    return state  # Returns same object (mutated)
```

**Problems:**
- ❌ Mutates input state (violates immutability principle)
- ❌ Returns full state object (not partial update)
- ❌ Uses `.stash()` helper method (YAGNI - unnecessary abstraction)
- ❌ No fail-fast validation
- ❌ Incompatible with LangGraph StateGraph pattern

---

### After (New TypedDict Pattern)

```python
import logging
from typing import Dict, Any
from src.state.conversation_state import ConversationState  # NEW TypedDict

logger = logging.getLogger(__name__)


def classify_query(state: ConversationState) -> Dict[str, Any]:
    """LangGraph pattern: Returns partial state update dict.

    Node Signature (LangGraph Pattern):
        - Accepts: ConversationState (TypedDict with all conversation data)
        - Returns: Dict[str, Any] (PARTIAL update with only modified fields)

    Design Principles:
        - Fail-Fast (Defensibility): Validates required fields before processing
        - Pure Logic Extraction (Maintainability): Business logic in helper functions
        - Loose Coupling: Returns dict update, doesn't modify input state

    Args:
        state: Current conversation state with the user's query

    Returns:
        Partial state update dict with classification results

    Raises:
        ValueError: If required fields (query, role) are missing
    """
    # 1. FAIL-FAST VALIDATION (Defensibility principle)
    try:
        query = state["query"]  # Direct access fails fast if missing
        role = state.get("role", "Developer")  # Optional with default
    except KeyError as e:
        logger.error(f"classify_query: Missing required field: {e}")
        return {
            "error": "classification_failed",
            "error_message": f"Missing required field: {e}"
        }

    # 2. INITIALIZE PARTIAL UPDATE DICT (only fields we're modifying)
    update: Dict[str, Any] = {}

    # 3. BUSINESS LOGIC (extract to pure functions when complex)
    lowered = query.lower()

    if "technical" in lowered:
        update["query_type"] = "technical"

    # 4. RETURN ONLY MODIFIED FIELDS (LangGraph merges with existing state)
    return update
```

**Benefits:**
- ✅ Input state remains unchanged (immutability)
- ✅ Returns only modified fields (efficient partial updates)
- ✅ Direct dict access (KISS/YAGNI - no helper methods needed)
- ✅ Fail-fast validation (Defensibility principle)
- ✅ Compatible with LangGraph StateGraph

---

## Step-by-Step Migration Checklist

### Step 1: Update Imports

```python
# OLD
from src.state.conversation_state import ConversationState

# NEW
import logging
from typing import Dict, Any
from src.state.conversation_state import ConversationState

logger = logging.getLogger(__name__)
```

---

### Step 2: Update Function Signature

```python
# OLD
def my_node(state: ConversationState) -> ConversationState:

# NEW
def my_node(state: ConversationState) -> Dict[str, Any]:
```

---

### Step 3: Add Fail-Fast Validation

```python
# At the top of function body
try:
    # Required fields: Use direct bracket access (fails fast)
    query = state["query"]
    role = state["role"]

    # Optional fields: Use .get() with defaults
    chat_history = state.get("chat_history", [])
except KeyError as e:
    logger.error(f"my_node: Missing required field: {e}")
    return {
        "error": "node_failed",
        "error_message": f"Missing required field: {e}"
    }
```

---

### Step 4: Initialize Partial Update Dict

```python
# Initialize empty update dict
update: Dict[str, Any] = {}
```

---

### Step 5: Replace State Mutation with Dict Updates

```python
# OLD (mutation)
state.stash("key", "value")
state.set_answer("response")
state.add_retrieved_chunks(chunks)

# NEW (dict updates)
update["key"] = "value"
update["answer"] = "response"
update["retrieved_chunks"] = chunks
```

---

### Step 6: Replace State Access with Dict Access

```python
# OLD
value = state.fetch("key", default)
query_type = state.extras.get("query_type")

# NEW
value = state.get("key", default)  # Direct dict.get()
query_type = state.get("query_type")
```

---

### Step 7: Return Partial Update

```python
# OLD
return state  # Returns full mutated state

# NEW
return update  # Returns only modified fields
```

---

## Common Patterns

### Pattern 1: Conditional Field Updates

```python
def my_node(state: ConversationState) -> Dict[str, Any]:
    update: Dict[str, Any] = {}

    query = state["query"]
    lowered = query.lower()

    # Only add field if condition met
    if "code" in lowered:
        update["code_requested"] = True

    if "data" in lowered:
        update["data_requested"] = True

    # Always set query_type
    update["query_type"] = "technical" if "code" in lowered else "general"

    return update  # May return 1, 2, or 3 fields depending on conditions
```

---

### Pattern 2: List Appending (Immutably)

```python
def my_node(state: ConversationState) -> Dict[str, Any]:
    # Get existing list (don't mutate!)
    current_signals = state.get("hiring_signals", [])

    # Create NEW list (immutable pattern)
    updated_signals = current_signals + ["new_signal"]

    return {"hiring_signals": updated_signals}
```

**❌ WRONG (mutates input state):**
```python
signals = state.get("hiring_signals", [])
signals.append("new_signal")  # IN-PLACE MUTATION!
return {"hiring_signals": signals}  # Original state now mutated!
```

---

### Pattern 3: Complex Logic Extraction

```python
def _classify_query_type(query: str, role: str) -> str:
    """Pure helper function - easy to test, no side effects."""
    lowered = query.lower()

    if "code" in lowered:
        return "technical"
    elif "career" in lowered:
        return "career"
    else:
        return "general"


def classify_query(state: ConversationState) -> Dict[str, Any]:
    """Node wraps pure logic with I/O and validation."""
    try:
        query = state["query"]
        role = state.get("role", "Developer")
    except KeyError as e:
        return {"error": "classification_failed", "error_message": str(e)}

    # Delegate to pure function
    query_type = _classify_query_type(query, role)

    return {"query_type": query_type}
```

**Benefits:**
- Pure function is easy to unit test
- Business logic separated from I/O
- Follows Maintainability principle

---

### Pattern 4: Error Handling (Graceful Degradation)

```python
def my_node(state: ConversationState) -> Dict[str, Any]:
    try:
        query = state["query"]
    except KeyError as e:
        # Fail-fast: Required field missing
        return {
            "error": "missing_field",
            "error_message": f"Required field missing: {e}"
        }

    try:
        # Attempt expensive operation
        result = expensive_llm_call(query)
    except Exception as e:
        # Fail-safe: Graceful degradation
        logger.warning(f"LLM call failed: {e}")
        return {
            "answer": "I encountered an issue processing that query.",
            "error": "llm_degraded",
            "error_message": str(e)
        }

    return {"answer": result}
```

---

## Testing Strategy

### Test 1: Node Signature Compliance

```python
def test_accepts_typed_dict_state():
    """Should accept ConversationState TypedDict as input."""
    state: ConversationState = {
        "query": "test",
        "role": "Developer",
        "session_id": "123"
    }

    result = my_node(state)
    assert isinstance(result, dict)


def test_returns_partial_update_not_full_state():
    """Should return only modified fields, not full state."""
    state: ConversationState = {
        "query": "test",
        "role": "Developer",
        "session_id": "123",
        "chat_history": []
    }

    result = my_node(state)

    # Should NOT return unchanged fields
    assert "query" not in result
    assert "session_id" not in result
    assert "chat_history" not in result


def test_does_not_mutate_input_state():
    """Should not modify input state (immutability)."""
    state: ConversationState = {"query": "test", "role": "Dev"}
    original = state.copy()

    my_node(state)

    assert state == original  # Unchanged
```

---

### Test 2: Fail-Fast Validation

```python
def test_handles_missing_required_field():
    """Should fail-fast with clear error when required field missing."""
    state: ConversationState = {"role": "Dev"}  # Missing "query"

    result = my_node(state)

    assert result["error"] == "node_failed"
    assert "query" in result["error_message"].lower()


def test_handles_empty_state():
    """Should gracefully handle completely empty state."""
    state: ConversationState = {}

    result = my_node(state)

    assert "error" in result
```

---

### Test 3: Business Logic

```python
def test_classification_logic():
    """Should correctly classify queries."""
    state: ConversationState = {
        "query": "How does RAG work?",
        "role": "Developer"
    }

    result = my_node(state)

    assert result["query_type"] == "technical"
    assert result.get("teaching_moment") is True
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Forgetting to Initialize `update` Dict

**❌ Wrong:**
```python
def my_node(state: ConversationState) -> Dict[str, Any]:
    if condition:
        return {"key": "value"}
    # What if condition is False? No return!
```

**✅ Correct:**
```python
def my_node(state: ConversationState) -> Dict[str, Any]:
    update: Dict[str, Any] = {}  # Always initialize

    if condition:
        update["key"] = "value"

    return update  # Always returns dict (even if empty)
```

---

### Pitfall 2: Mutating Lists In-Place

**❌ Wrong:**
```python
signals = state.get("hiring_signals", [])
signals.append("new")  # Mutates original!
return {"hiring_signals": signals}
```

**✅ Correct:**
```python
current = state.get("hiring_signals", [])
updated = current + ["new"]  # New list
return {"hiring_signals": updated}
```

---

### Pitfall 3: Using Old `.stash()` / `.fetch()` Methods

**❌ Wrong:**
```python
state.stash("key", "value")  # Dataclass method doesn't exist on TypedDict!
```

**✅ Correct:**
```python
update["key"] = "value"  # Direct dict assignment
```

---

### Pitfall 4: Accessing Optional Fields Without `.get()`

**❌ Wrong:**
```python
answer = state["answer"]  # KeyError if not set yet!
```

**✅ Correct:**
```python
answer = state.get("answer", "No answer yet")  # Safe with default
```

---

## Migration Verification

After migrating a node, run:

```bash
# 1. Run TypedDict structural tests
pytest tests/test_conversation_state.py -v

# 2. Run node-specific tests
pytest tests/test_my_node_migration.py -v

# 3. Run integration tests
pytest tests/test_conversation_quality.py -v
```

**Success Criteria:**
- ✅ All TypedDict tests pass (23/23)
- ✅ Node signature tests pass (accepts TypedDict, returns Dict, doesn't mutate)
- ✅ Fail-fast validation tests pass
- ✅ Business logic tests pass
- ✅ Integration tests pass (node works in pipeline)

---

## Next Steps After POC

1. ✅ **Phase 3B Complete:** `classify_query` migrated (20/20 tests passing)
2. ⏳ **Phase 3C:** Document pattern (this guide)
3. ⏳ **Phase 3D:** Migrate remaining 14 nodes following this pattern
4. ⏳ **Phase 4:** Implement StateGraph orchestration

---

## Questions or Issues?

**If you encounter:**
- **Type errors:** Ensure using `from src.state.conversation_state import ConversationState` (NEW TypedDict)
- **Attribute errors** (`'dict' object has no attribute 'stash'`): You're trying to use old dataclass methods - use dict methods instead
- **Test failures:** Check that you're returning partial updates (not full state) and not mutating input

**Design Principles Reference:**
- See [QA_STRATEGY.md § Design Principles](QA_STRATEGY.md#design-principles-for-langgraph-migration) for detailed explanations
- See [QA_LANGGRAPH_MIGRATION.md](QA_LANGGRAPH_MIGRATION.md) for migration-specific standards
