# LangGraph Migration - QA Policy & Standards

**Date:** October 17, 2025
**Purpose:** Define quality standards for migrating from functional pipeline to actual LangGraph library
**Status:** 🚧 IN PROGRESS - Phase 1 (QA Policy Updates)

**📚 Related Documentation:**
- **Design Principles (Detailed)**: [QA_STRATEGY.md § Design Principles](QA_STRATEGY.md#design-principles-for-langgraph-migration) - Comprehensive explanations with LangGraph-specific examples
- **QA Strategy**: [QA_STRATEGY.md](QA_STRATEGY.md) - Master QA documentation
- **Test Status**: [QA_STRATEGY.md § Current Test Status](QA_STRATEGY.md#current-test-status) - 77 tests, 99% pass rate

---

## Migration Overview

**From:** Functional pipeline (tuple of lambdas, for loop)
**To:** LangGraph `StateGraph` with `.compile()` pattern
**Reference Implementation:** [Tech With Tim - Advanced-Langflow-Web-Agent](https://github.com/techwithtim/Advanced-Langflow-Web-Agent)
**Estimated Effort:** 16-18 hours across 7 phases

---

## Design Principles (from QUICK_REFERENCE.md)

### **1. Single Responsibility Principle (SRP)** ✅ APPLIES TO LANGGRAPH

**Rule:** Each node should have ONE clear responsibility

**Example:**
```python
# ✅ Good: Single responsibility
def classify_query(state: ConversationState) -> ConversationState:
    """ONLY classifies query type, nothing else."""
    query_type = determine_type(state["query"])
    return {"query_type": query_type}

# ❌ Bad: Multiple responsibilities
def classify_and_retrieve(state: ConversationState) -> ConversationState:
    """Does TWO things - violates SRP."""
    query_type = determine_type(state["query"])
    chunks = retrieve_from_db(state["query"])  # Should be separate node!
    return {"query_type": query_type, "chunks": chunks}
```

**Migration Rule:** Keep existing node separation (classify → retrieve → generate → plan → execute)

---

### **2. Encapsulation & Abstraction** ✅ APPLIES TO LANGGRAPH

**Rule:** Hide implementation details, expose clean interfaces

**Example:**
```python
# ✅ Good: Encapsulated node
def retrieve_chunks(state: ConversationState) -> ConversationState:
    """Public interface - implementation hidden."""
    try:
        chunks = _fetch_from_pgvector(state["query"])  # Private helper
        return {"retrieved_chunks": chunks}
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return {"retrieved_chunks": [], "error": "retrieval_failed"}

def _fetch_from_pgvector(query: str) -> List[Dict]:
    """Private implementation - users don't see this."""
    # Complex pgvector logic here
    pass
```

**Migration Rule:** Node functions remain public, extract complex logic to private helpers

---

### **3. Loose Coupling** ✅ CRITICAL FOR LANGGRAPH

**Rule:** Nodes communicate ONLY via state, not direct function calls

**Example:**
```python
# ✅ Good: Loose coupling via state
def classify_query(state: ConversationState) -> ConversationState:
    return {"query_type": "technical"}  # Output to state

def retrieve_chunks(state: ConversationState) -> ConversationState:
    query_type = state["query_type"]  # Input from state
    # ...

# ❌ Bad: Tight coupling via direct calls
def classify_query(state: ConversationState) -> ConversationState:
    result = {"query_type": "technical"}
    retrieve_chunks(result)  # DON'T DO THIS! Bypasses graph orchestration
    return result
```

**Migration Rule:** NO direct node-to-node function calls. All communication via state updates.

---

### **4. Defensibility (Fail-Fast, Fail-Safe)** ✅ CRITICAL FOR LANGGRAPH

**Rule:** Validate inputs, handle errors gracefully, never crash the graph

**Fail-Fast (Validate Early):**
```python
def generate_answer(state: ConversationState) -> ConversationState:
    # Fail-fast: Validate before expensive operations
    if not state.get("retrieved_chunks"):
        return {
            "answer": "I don't have enough information to answer that.",
            "error": "no_chunks"
        }

    if not state.get("query"):
        raise ValueError("Query cannot be empty")  # Fail-fast on invalid input

    # Proceed with expensive LLM call
    answer = llm.invoke(state["query"], chunks=state["retrieved_chunks"])
    return {"answer": answer}
```

**Fail-Safe (Graceful Degradation):**
```python
def execute_actions(state: ConversationState) -> ConversationState:
    """Never crash - degrade gracefully if services unavailable."""
    try:
        if state.get("send_email"):
            resend_service.send(state["email_data"])
    except Exception as e:
        logger.warning(f"Email failed (degraded mode): {e}")
        # DON'T raise - continue execution
        return {"email_sent": False, "email_error": str(e)}

    return {"email_sent": True}
```

**Migration Rule:** Every node MUST handle errors gracefully. Graph should never crash.

---

### **5. Maintainability & Testability** ✅ APPLIES TO LANGGRAPH

**Rule:** Pure functions when possible, separate I/O from logic

**Example:**
```python
# ✅ Good: Pure business logic (easy to test)
def _calculate_hiring_signals(query: str, role: str) -> List[str]:
    """Pure function - deterministic, no side effects."""
    signals = []
    if "hiring" in query.lower():
        signals.append("mentioned_hiring")
    if role == "Hiring Manager (technical)":
        signals.append("technical_role")
    return signals

# Node wraps pure logic with I/O
def detect_hiring_signals(state: ConversationState) -> ConversationState:
    """Node handles I/O, delegates to pure function."""
    signals = _calculate_hiring_signals(state["query"], state["role"])
    return {"hiring_signals": signals}

# ❌ Bad: Logic mixed with I/O (hard to test)
def detect_hiring_signals(state: ConversationState) -> ConversationState:
    signals = []
    logger.info(f"Checking query: {state['query']}")  # I/O mixed with logic
    if "hiring" in state["query"].lower():
        signals.append("mentioned_hiring")
        supabase_analytics.log_event("hiring_signal")  # I/O mixed with logic
    return {"hiring_signals": signals}
```

**Migration Rule:** Extract pure logic to private functions. Nodes handle only I/O.

---

### **6. Simplicity (KISS, DRY, YAGNI)** ✅ APPLIES TO LANGGRAPH

**KISS - Keep It Simple:**
```python
# ✅ Good: Simple, readable
def should_retrieve(state: ConversationState) -> str:
    """Decide if retrieval needed."""
    if state.get("is_greeting"):
        return "skip_retrieval"
    return "retrieve"

# ❌ Bad: Over-engineered
def should_retrieve(state: ConversationState) -> str:
    """Complex logic for simple decision."""
    retrieval_decision_matrix = {
        ("greeting", True): "skip_retrieval",
        ("greeting", False): "retrieve",
        # ... 20 more combinations
    }
    key = (state.get("query_type"), state.get("is_greeting"))
    return retrieval_decision_matrix.get(key, "retrieve")
```

**DRY - Don't Repeat Yourself:**
```python
# ✅ Good: Reusable error handler
def _handle_node_error(node_name: str, error: Exception, state: ConversationState) -> Dict:
    """Centralized error handling for all nodes."""
    logger.error(f"{node_name} failed: {error}")
    return {"error": f"{node_name}_failed", "error_message": str(error)}

def classify_query(state: ConversationState) -> ConversationState:
    try:
        # ... classification logic
        pass
    except Exception as e:
        return _handle_node_error("classify_query", e, state)

# ❌ Bad: Repeated error handling
def classify_query(state: ConversationState) -> ConversationState:
    try:
        pass
    except Exception as e:
        logger.error(f"classify_query failed: {e}")  # Repeated in every node!
        return {"error": "classify_query_failed"}
```

**YAGNI - You Aren't Gonna Need It:**
```python
# ✅ Good: Add features when needed
graph_builder = StateGraph(ConversationState)
graph_builder.add_node("classify", classify_query)
graph_builder.add_node("retrieve", retrieve_chunks)
# Only the nodes we actually use

# ❌ Bad: Future-proofing for hypothetical features
graph_builder.add_node("classify", classify_query)
graph_builder.add_node("sentiment_analysis", sentiment_analysis)  # Not used yet!
graph_builder.add_node("language_detection", detect_language)  # Might need later?
graph_builder.add_node("spam_filter", filter_spam)  # Just in case?
```

**Migration Rule:** Port only existing functionality. No new features during migration.

---

## LangGraph-Specific Quality Standards

### **Standard 1: StateGraph Structure**

**Rule:** Use `StateGraph` with `TypedDict`, compile before use

**Example:**
```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages

# ✅ Correct TypedDict definition
class ConversationState(TypedDict, total=False):
    """State passed between LangGraph nodes."""
    query: str
    role: str
    chat_history: Annotated[list, add_messages]  # Special annotation for message lists
    retrieved_chunks: List[Dict[str, Any]]
    answer: str
    # ... 10 more fields

# ✅ Correct StateGraph usage
graph_builder = StateGraph(ConversationState)
graph_builder.add_node("classify", classify_query)
graph_builder.add_node("retrieve", retrieve_chunks)
graph_builder.add_edge(START, "classify")
graph_builder.add_edge("classify", "retrieve")
graph = graph_builder.compile()

# ❌ Wrong: Forgot to compile
graph_builder = StateGraph(ConversationState)
# ... add nodes and edges ...
result = graph_builder.invoke(state)  # ERROR! Must compile first
```

**Test:**
```python
def test_graph_is_compiled():
    """Ensure graph is compiled before use."""
    from src.flows.conversation_flow import graph
    assert hasattr(graph, "invoke"), "Graph must be compiled (have .invoke())"
    assert hasattr(graph, "stream"), "Compiled graph has .stream()"
```

---

### **Standard 2: Node Function Signatures**

**Rule:** All nodes accept `ConversationState`, return `Dict` (partial state update)

**Example:**
```python
# ✅ Correct signature
def classify_query(state: ConversationState) -> Dict[str, Any]:
    """Classify user query type."""
    query_type = _determine_type(state["query"])
    return {"query_type": query_type}  # Returns PARTIAL state update

# ❌ Wrong: Returns full state
def classify_query(state: ConversationState) -> ConversationState:
    query_type = _determine_type(state["query"])
    state["query_type"] = query_type  # Don't mutate!
    return state  # Don't return full state!

# ❌ Wrong: Returns value directly
def classify_query(state: ConversationState) -> str:
    return _determine_type(state["query"])  # Must return Dict!
```

**Test:**
```python
def test_node_returns_partial_state():
    """Ensure nodes return partial state updates."""
    state = {"query": "test", "role": "Developer"}
    result = classify_query(state)

    assert isinstance(result, dict), "Node must return dict"
    assert "query_type" in result, "Node must return new keys"
    assert "query" not in result, "Node should NOT return unchanged keys"
```

---

### **Standard 3: Error Handling in Nodes**

**Rule:** Every node MUST have try/except, return error state on failure

**Example:**
```python
# ✅ Correct error handling
def retrieve_chunks(state: ConversationState) -> Dict[str, Any]:
    """Retrieve relevant chunks from pgvector."""
    try:
        chunks = rag_engine.retrieve(state["query"], top_k=4)
        return {"retrieved_chunks": chunks.get("chunks", [])}

    except Exception as e:
        logger.error(f"Retrieval failed: {e}", extra={
            "query": state.get("query"),
            "role": state.get("role")
        })

        # Graceful degradation: Return empty chunks instead of crashing
        return {
            "retrieved_chunks": [],
            "error": "retrieval_failed",
            "error_message": "Unable to retrieve information at this time."
        }

# ❌ Wrong: No error handling
def retrieve_chunks(state: ConversationState) -> Dict[str, Any]:
    chunks = rag_engine.retrieve(state["query"], top_k=4)  # Can crash!
    return {"retrieved_chunks": chunks.get("chunks", [])}
```

**Test:**
```python
def test_node_handles_errors_gracefully():
    """Ensure nodes don't crash on errors."""
    with patch('src.core.rag_engine.RagEngine.retrieve', side_effect=Exception("DB down")):
        state = {"query": "test"}
        result = retrieve_chunks(state)

        assert "error" in result, "Node must set error flag"
        assert result["retrieved_chunks"] == [], "Node must provide fallback"
        assert "error_message" in result, "Node must explain error"
```

---

### **Standard 4: Conditional Edges**

**Rule:** Use conditional edges for branching logic, not if statements in nodes

**Example:**
```python
# ✅ Correct: Conditional edge handles branching
def should_retrieve(state: ConversationState) -> str:
    """Decide next node based on state."""
    if state.get("is_greeting"):
        return "skip_to_answer"  # Skip retrieval for greetings
    if state.get("resume_explicitly_requested"):
        return "handle_resume"  # Skip RAG for explicit requests
    return "retrieve"  # Default path

graph_builder.add_conditional_edges(
    "classify",
    should_retrieve,
    {
        "retrieve": "retrieve_chunks",
        "skip_to_answer": "generate_answer",
        "handle_resume": "handle_resume_request"
    }
)

# ❌ Wrong: Branching inside node (loses graph visibility)
def classify_and_maybe_retrieve(state: ConversationState) -> Dict:
    if state.get("is_greeting"):
        # Do greeting logic inline
        return {"answer": "Hello! How can I help?"}
    else:
        # Do retrieval inline
        chunks = rag_engine.retrieve(state["query"])
        return {"retrieved_chunks": chunks}
```

**Test:**
```python
def test_conditional_edge_routing():
    """Ensure conditional edges route correctly."""
    # Greeting path
    state1 = {"query": "hello", "is_greeting": True}
    next_node = should_retrieve(state1)
    assert next_node == "skip_to_answer"

    # Normal path
    state2 = {"query": "explain RAG", "is_greeting": False}
    next_node = should_retrieve(state2)
    assert next_node == "retrieve"
```

---

### **Standard 5: State Immutability**

**Rule:** NEVER mutate input state, always return new dict

**Example:**
```python
# ✅ Correct: Returns new dict
def add_timestamp(state: ConversationState) -> Dict[str, Any]:
    from datetime import datetime
    return {"timestamp": datetime.now().isoformat()}

# ❌ Wrong: Mutates input state
def add_timestamp(state: ConversationState) -> Dict[str, Any]:
    state["timestamp"] = datetime.now().isoformat()  # MUTATION!
    return state
```

**Test:**
```python
def test_node_does_not_mutate_state():
    """Ensure nodes don't mutate input state."""
    original_state = {"query": "test", "role": "Developer"}
    state_copy = original_state.copy()

    result = classify_query(original_state)

    assert original_state == state_copy, "Node must not mutate input state"
```

---

### **Standard 6: Observable Node Execution**

**Rule:** All nodes MUST log execution to LangSmith

**Example:**
```python
from src.observability import trace_generation

# ✅ Correct: Decorated for observability
@trace_generation(name="classify_query")
def classify_query(state: ConversationState) -> Dict[str, Any]:
    """Classify user query type."""
    query_type = _determine_type(state["query"])
    return {"query_type": query_type}

# ❌ Wrong: No observability
def classify_query(state: ConversationState) -> Dict[str, Any]:
    query_type = _determine_type(state["query"])
    return {"query_type": query_type}
```

**Test:**
```python
def test_node_is_traced():
    """Ensure node execution is traced."""
    from unittest.mock import patch

    with patch('langsmith.Client.create_run') as mock_trace:
        state = {"query": "test"}
        classify_query(state)

        assert mock_trace.called, "Node must create trace"
        assert "classify_query" in str(mock_trace.call_args)
```

---

## Migration Checklist

### **Phase 1: QA Policy Updates** ✅ IN PROGRESS
- [x] Document design principles (SRP, Encapsulation, Loose Coupling, Defensibility, Maintainability, Simplicity)
- [x] Define LangGraph-specific standards (StateGraph, Node Signatures, Error Handling, Conditional Edges, Immutability, Observability)
- [ ] Add test templates for each standard
- [ ] Update QA_STRATEGY.md with migration standards
- [ ] Get user approval before Phase 2

### **Phase 2: Study Reference Implementation**
- [ ] Clone Tech With Tim repo
- [ ] Document error handling patterns
- [ ] Document TypedDict usage
- [ ] Document StateGraph compilation pattern
- [ ] Document conditional edge patterns
- [ ] Identify gaps vs our requirements

### **Phase 3: State Management Migration** ✅ IN PROGRESS
- [x] Create new `ConversationState` TypedDict (src/state/conversation_state.py, 230 lines)
- [x] Add `Annotated[list, add_messages]` for chat_history
- [x] ~~Create `StateHelper` class~~ SKIPPED (YAGNI principle - Python dict methods sufficient)
- [x] Update all 15 state fields with proper types
- [x] Write tests for state immutability (tests/test_conversation_state.py, 23/23 passing)
- [x] **POC Migration:** classify_query node migrated (tests/test_classify_query_migration.py, 20/20 passing)
- [x] **Migration Guide:** Created docs/NODE_MIGRATION_GUIDE.md (proven pattern documented)
- [ ] Migrate remaining 14 nodes following POC pattern (see NODE_MIGRATION_GUIDE.md)

### **Phase 4: Graph Construction**
- [ ] Replace functional pipeline with `StateGraph`
- [ ] Add all 8 nodes via `.add_node()`
- [ ] Add linear edges with `.add_edge()`
- [ ] Add conditional edges for branching (greeting detection, resume requests)
- [ ] Compile graph with `.compile()`
- [ ] Add comprehensive error handling to each node
- [ ] Update `conversation_flow.py` docstring

### **Phase 5: Test Updates**
- [ ] Update `test_conversation_quality.py` (19 tests)
- [ ] Update `test_resume_distribution.py` (37 tests)
- [ ] Update `test_error_handling.py` (6 tests)
- [ ] Update `test_documentation_alignment.py` (15 tests)
- [ ] Add new LangGraph-specific tests (6 new tests)
- [ ] Ensure 99% pass rate maintained (82/83 tests)

### **Phase 6: Documentation Updates**
- [ ] Update master docs (SYSTEM_ARCHITECTURE_SUMMARY.md, PROJECT_REFERENCE_OVERVIEW.md)
- [ ] Update feature docs (DISPLAY_INTELLIGENCE_IMPLEMENTATION.md, etc.)
- [ ] Update API docs (API_SETUP_GUIDE.md)
- [ ] Update user-facing responses (response_generator.py, content_blocks.py)
- [ ] Run documentation alignment tests (15 tests)

### **Phase 7: Deploy & Verify**
- [ ] Deploy to Vercel preview
- [ ] Run production smoke tests
- [ ] Monitor LangSmith traces
- [ ] Verify no latency regressions
- [ ] Verify no error rate increases
- [ ] Update CHANGELOG.md
- [ ] Create Architecture Decision Record (ADR)

---

## Success Criteria

### **Code Quality:**
- [ ] All nodes have type hints (`ConversationState` → `Dict[str, Any]`)
- [ ] All nodes have try/except with graceful degradation
- [ ] All nodes are decorated with `@trace_generation`
- [ ] No direct node-to-node function calls (loose coupling)
- [ ] StateGraph properly compiled before use
- [ ] Conditional edges used for branching (not if statements in nodes)

### **Test Quality:**
- [ ] 99% pass rate maintained (82/83 tests, 1 skipped)
- [ ] New tests added for LangGraph standards (6 tests)
- [ ] All tests use actual compiled graph (not mocks)
- [ ] Error handling tests verify graceful degradation

### **Documentation Quality:**
- [ ] All 50+ "LangGraph" references accurate
- [ ] Master docs updated with StateGraph architecture
- [ ] Feature docs updated with node-based flow
- [ ] User-facing responses claim "LangGraph" truthfully
- [ ] Documentation alignment tests pass (14/15, 93%)

### **Production Quality:**
- [ ] No latency regressions (p95 < 3s maintained)
- [ ] No error rate increase (0% maintained)
- [ ] LangSmith traces show graph structure
- [ ] Vercel deployment successful

---

## Rollback Plan

If migration fails or causes production issues:

1. **Immediate:** Revert to functional pipeline (git revert)
2. **Communication:** Update docs to clarify "LangGraph-inspired" vs "LangGraph library"
3. **Analysis:** Document failure reasons
4. **Decision:** Retry migration with fixes OR accept functional pipeline and update naming

---

**Status:** Phase 1 complete, awaiting user approval for Phase 2
**Next:** Study Tech With Tim implementation, create migration plan
