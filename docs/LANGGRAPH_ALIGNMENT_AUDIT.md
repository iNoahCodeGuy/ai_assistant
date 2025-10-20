# LangGraph Alignment Audit

**Date**: October 19, 2025
**Purpose**: Compare Portfolia's current TypedDict pipeline to LangGraph best practices from techwithtim tutorials
**Status**: 🔴 Misaligned - Not using StateGraph

## Executive Summary

**Critical Finding**: Portfolia is **NOT using LangGraph** — we're using a **custom functional pipeline** that mimics some LangGraph patterns but lacks the framework's core benefits.

**Risk Level**: 🟡 Medium
- Current system works and is maintainable
- But we're missing LangGraph's built-in benefits (debugging tools, conditional routing, persistence)
- Marketing claims "LangGraph orchestration" but implementation is custom

**Recommendation**: Either:
1. **Rebrand** as "LangGraph-inspired pipeline" (honest, low effort)
2. **Migrate** to actual StateGraph (correct, high effort)

---

## Current Implementation vs LangGraph Best Practices

### 1. State Management

#### ❌ Current (Portfolia)
```python
# src/state/conversation_state.py
from typing import TypedDict, List, Dict, Any, Optional

class ConversationState(TypedDict, total=False):
    """TypedDict for conversation state (NOT a StateGraph)"""
    query: str
    role: str
    answer: str
    chat_history: List[Dict[str, str]]
    # ... 30+ fields
```

**Issues**:
- Manual state updates via `state.update(dict)`
- No automatic state merging or reduction
- No schema validation at runtime
- TypedDict doesn't enforce required fields at runtime (only type hints)

#### ✅ LangGraph Best Practice (techwithtim)
```python
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated
from operator import add

class State(TypedDict):
    messages: Annotated[List, add]  # Automatic list merging
    query: str
    answer: Optional[str]

# StateGraph handles merging automatically
graph = StateGraph(State)
```

**Benefits**:
- Automatic state merging with `Annotated` types
- Schema validation at runtime
- Built-in state history/checkpointing
- Cleaner node signatures (nodes return partial updates)

---

### 2. Node Signatures

#### ❌ Current (Portfolia)
```python
# src/flows/conversation_nodes.py
def classify_query(state: ConversationState) -> Dict[str, Any]:
    """Node that manually updates state dict"""
    update = {}
    update["query_type"] = "technical"
    state.update(update)  # Manual merge
    return state  # Returns ENTIRE state
```

**Issues**:
- Nodes receive AND return entire state dict (verbose)
- Manual state merging (error-prone)
- No automatic partial updates
- Node signature doesn't match LangGraph convention

#### ✅ LangGraph Best Practice (techwithtim)
```python
def classify_node(state: State) -> dict:
    """Node returns PARTIAL state update"""
    return {"query_type": "technical"}  # StateGraph merges automatically

# StateGraph handles the merge
graph.add_node("classify", classify_node)
```

**Benefits**:
- Nodes are pure functions (input state → partial update)
- Framework handles merging
- Cleaner, more testable code

---

### 3. Pipeline Definition

#### ❌ Current (Portfolia)
```python
# src/flows/conversation_flow.py
def run_conversation_flow(state, rag_engine, session_id):
    """Custom linear pipeline execution"""
    pipeline = [
        lambda s: handle_greeting(s, rag_engine),
        lambda s: classify_query(s),
        lambda s: retrieve_chunks(s, rag_engine) if not s.get("is_greeting") else s,
        lambda s: generate_answer(s, rag_engine) if not s.get("is_greeting") else s,
        lambda s: plan_actions(s),
        lambda s: apply_role_context(s),
        lambda s: execute_actions(s, rag_engine, session_id),
        lambda s: log_and_notify(s, session_id),
    ]

    result = state
    for node_fn in pipeline:
        result = node_fn(result)
    return result
```

**Issues**:
- No actual LangGraph StateGraph
- Manual conditional execution with lambdas
- No debugging/visualization tools
- No automatic checkpointing
- Hard to modify flow (requires code changes)

#### ✅ LangGraph Best Practice (techwithtim)
```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(State)

# Add nodes
workflow.add_node("greeting", handle_greeting)
workflow.add_node("classify", classify_query)
workflow.add_node("retrieve", retrieve_chunks)
workflow.add_node("generate", generate_answer)

# Define edges (conditional routing)
workflow.set_entry_point("greeting")

def should_retrieve(state):
    return "retrieve" if not state.get("is_greeting") else "generate"

workflow.add_conditional_edges("greeting", should_retrieve)
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

# Compile graph
app = workflow.compile()

# Execute with built-in debugging
result = app.invoke(initial_state)
```

**Benefits**:
- Visual debugging with LangSmith
- Automatic checkpointing/persistence
- Conditional routing defined declaratively
- Easy to modify flow without code changes

---

### 4. Error Handling

#### ❌ Current (Portfolia)
```python
# Manual try/except in each node
def generate_answer(state, rag_engine):
    try:
        answer = rag_engine.generate_response(...)
        state["answer"] = answer
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        state["answer"] = "Sorry, I encountered an error."
    return state
```

**Issues**:
- Repeated error handling in every node
- No framework-level error recovery
- Hard to implement retry logic

#### ✅ LangGraph Best Practice
```python
from langgraph.checkpoint import MemorySaver

# StateGraph supports automatic checkpointing
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# Can retry from last checkpoint on error
result = app.invoke(state, config={"configurable": {"thread_id": "123"}})
```

**Benefits**:
- Framework handles checkpointing
- Easy to implement retry logic
- Better error recovery

---

### 5. Observability

#### ⚠️ Current (Portfolia) - Partial
```python
# Manual LangSmith tracing with decorators
from src.observability.langsmith_traces import trace_generation

@trace_generation
def generate_answer(state, rag_engine):
    # Manually instrumented
    ...
```

**Status**: We DO use LangSmith, but manually instrumented

#### ✅ LangGraph Best Practice
```python
# StateGraph automatically traces to LangSmith
app = workflow.compile()
result = app.invoke(state)  # Automatic tracing, no decorators needed
```

**Benefits**:
- Zero-effort tracing
- Automatic visualization in LangSmith
- Better debugging experience

---

## Alignment Score by Category

| Category | Current Score | Max Score | Status |
|----------|--------------|-----------|--------|
| State Management | 3/10 | 10 | 🔴 TypedDict, not StateGraph |
| Node Signatures | 5/10 | 10 | 🟡 Returns entire state, not partial |
| Pipeline Definition | 2/10 | 10 | 🔴 No StateGraph, manual execution |
| Conditional Routing | 4/10 | 10 | 🟡 Lambdas instead of add_conditional_edges |
| Error Handling | 4/10 | 10 | 🟡 Manual try/except, no checkpointing |
| Observability | 6/10 | 10 | 🟡 LangSmith manual, not auto |
| **Overall** | **24/60** | **60** | **🔴 40% aligned** |

---

## References Used

**techwithtim tutorials analyzed**:
1. ✅ https://github.com/techwithtim/LangGraph-Tutorial.git
   - Basic StateGraph patterns
   - Node signatures (partial state returns)
   - Conditional edges

2. ✅ https://github.com/techwithtim/Advanced-Langflow-Web-Agent.git
   - Complex routing logic
   - Tool integration patterns
   - State persistence

3. ✅ https://github.com/techwithtim/Advanced-Research-Agent.git
   - Multi-step reasoning
   - Checkpointing strategies
   - Error recovery patterns

---

## Migration Path (If Desired)

### Option 1: Keep Current System (Rebrand)
**Effort**: 1 hour
**Changes**:
- Update docs to say "LangGraph-inspired pipeline"
- Update greetings to say "LLM orchestration" not "LangGraph orchestration"
- No code changes

**Pros**: Honest, works, maintainable
**Cons**: Not using actual LangGraph

### Option 2: Migrate to StateGraph
**Effort**: 16-24 hours
**Changes**:
1. Replace `ConversationState` TypedDict with StateGraph schema
2. Rewrite nodes to return partial updates
3. Replace `run_conversation_flow()` with `workflow.compile()`
4. Update all 91 tests to use StateGraph API
5. Add conditional routing with `add_conditional_edges()`
6. Enable checkpointing with MemorySaver

**Pros**: Actual LangGraph, better debugging, framework benefits
**Cons**: High effort, risk of breaking existing behavior

---

## Recommendation

**For now**: Keep current system (Option 1)

**Reasoning**:
1. Current system works well (91/93 tests = 98%)
2. LangGraph migration is high risk for modest benefit
3. More urgent priorities: Fix conversational personality, design principles review
4. Can migrate later when we have bandwidth

**Action**: Update documentation to accurately describe our architecture as "LangGraph-inspired functional pipeline" rather than claiming we use StateGraph.

---

## Next Steps

1. ✅ **Complete this audit** (DONE)
2. ⏳ **Update marketing materials** to say "LangGraph-inspired" not "LangGraph orchestration"
3. ⏳ **Add note to README**: "We use a functional pipeline inspired by LangGraph patterns. We may migrate to StateGraph in the future."
4. ⏳ **Continue with Todo #3**: Design principles review
5. ⏳ **Continue with Todo #4**: Cleanup audit

---

## Appendix: Current Flow Diagram

```
User Query
    ↓
[handle_greeting] → Check if "hello" → Return greeting (short-circuit)
    ↓ (if not greeting)
[classify_query] → Detect query type, expand vague queries, check ambiguous
    ↓
[extract_job_details] → Parse hiring manager queries for job info
    ↓
[retrieve_chunks] → pgvector search for relevant context
    ↓
[generate_answer] → LLM generation with RAG grounding
    ↓
[plan_actions] → Decide what side effects to trigger (email, SMS, analytics)
    ↓
[apply_role_context] → Add role-specific personality and formatting
    ↓
[execute_actions] → Run side effects (send emails, log analytics)
    ↓
[log_and_notify] → Final analytics logging
    ↓
Return to user
```

**Note**: This is a linear pipeline with conditional skips, not a StateGraph with conditional edges.
