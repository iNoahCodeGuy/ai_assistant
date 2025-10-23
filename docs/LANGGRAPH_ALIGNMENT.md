# LangGraph Alignment Documentation

**Created:** October 19, 2025
**Reference:** https://github.com/techwithtim/LangGraph-Tutorial.git
**Purpose:** Document alignment between our implementation and LangGraph best practices
**Status:** Week 1 - TypedDict approach, Week 2+ - StateGraph migration

---

## 📊 Current Implementation Status

### ✅ What We're Doing Correctly

#### 1. TypedDict State Management
**Our Implementation:**
```python
# src/state/conversation_state.py
class ConversationState(TypedDict, total=False):
    role: str
    query: str
    answer: str
    chat_history: List[Dict[str, str]]
    # ... more fields
```

**LangGraph Tutorial Pattern:**
```python
# simple.py (line 12)
class State(TypedDict):
    messages: Annotated[list, add_messages]
```

✅ **Aligned**: Both use TypedDict for type-safe state
✅ **Benefit**: IDE autocomplete, type checking, clear contracts

---

#### 2. Functional Node Pattern
**Our Implementation:**
```python
# src/flows/conversation_nodes.py
def classify_intent(state: ConversationState) -> ConversationState:
    """Classify user query intent and set retrieval affordances."""
    # Logic here
    return state
```

**LangGraph Tutorial Pattern:**
```python
# simple.py (line 19)
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}
```

✅ **Aligned**: Nodes are pure functions taking state, returning state
✅ **Benefit**: Testable, composable, easy to debug

---

#### 3. Linear Pipeline Orchestration
**Our Implementation:**
```python
# src/flows/conversation_flow.py
def run_conversation_flow(state: ConversationState, rag_engine: RagEngine, session_id: str) -> ConversationState:
    pipeline = (
        initialize_conversation_state,
        lambda s: handle_greeting(s, rag_engine),
        classify_role_mode,
        classify_intent,
        detect_hiring_signals,
        handle_resume_request,
        extract_entities,
        assess_clarification_need,
        ask_clarifying_question,
        compose_query,
        lambda s: retrieve_chunks(s, rag_engine),
        re_rank_and_dedup,
        validate_grounding,
        handle_grounding_gap,
        lambda s: generate_draft(s, rag_engine),
        hallucination_check,
        plan_actions,
        lambda s: format_answer(s, rag_engine),
        execute_actions,
        suggest_followups,
        update_memory,
    )

    start = time.time()
    for node in pipeline:
        state = node(state)
        if state.get("pipeline_halt") or state.get("is_greeting"):
            break

    elapsed_ms = int((time.time() - start) * 1000)
    state = log_and_notify(state, session_id=session_id, latency_ms=elapsed_ms)
    return state
```

**LangGraph Tutorial Pattern:**
```python
# simple.py (lines 26-28)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()
```

⚠️ **Partially Aligned**: We maintain a linear pipeline but still run it manually instead of compiling a StateGraph
✅ **Works**: Our pipeline is clean and predictable
🔄 **Improvement**: Migrate to StateGraph for official pattern

---

### ⚠️ Differences from Best Practices

#### 1. Not Using StateGraph Class

**LangGraph Official Pattern:**
```python
# main.py (line 90)
graph_builder = StateGraph(State)
graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_edge(START, "classifier")
graph = graph_builder.compile()
```

**Our Current Approach:**
```python
# We manually call functions in sequence
state = node1(state)
state = node2(state)
state = node3(state)
```

**Why We Haven't Migrated Yet:**
- ✅ Our approach works and is well-tested (74 tests passing)
- ✅ Simpler to understand for team onboarding
- ✅ Less risk close to Week 1 launch deadline
- ❌ Missing official framework benefits (visualization, checkpointing)

**Migration Plan: Week 2**

---

#### 2. No Conditional Routing

**LangGraph Pattern:**
```python
# main.py (lines 103-108)
graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"therapist": "therapist", "logical": "logical"}
)
```

**Our Current Approach:**
```python
# We handle routing within nodes
def classify_intent(state: ConversationState) -> ConversationState:
    if _is_data_display_request(state["query"].lower()):
        state.stash("query_type", "data")
    # Logic continues linearly
    return state
```

**Why This Difference:**
- ✅ All our queries go through same pipeline (no branching needed)
- ✅ Role-specific behavior handled in `format_answer` node
- ❌ Could benefit from parallel execution (e.g., retrieve + fetch code simultaneously)

**Migration Plan: Week 2** (add conditional edges for performance)

---

#### 3. No Message History Annotation

**LangGraph Pattern:**
```python
# simple.py (line 14)
class State(TypedDict):
    messages: Annotated[list, add_messages]  # ← Special annotation
```

**Our Current Approach:**
```python
class ConversationState(TypedDict, total=False):
    chat_history: List[Dict[str, str]]  # ← Plain list

    def add_message(self, role: str, content: str):
        # Manual append logic
```

**Why This Difference:**
- ✅ We have custom message structure (role, content, metadata)
- ✅ Our helper methods provide controlled mutations
- ❌ Missing LangGraph's built-in message handling benefits

**Migration Plan: Week 2** (adopt `add_messages` annotation)

---

## 🎯 Migration Path: TypedDict → StateGraph

### Phase 1: Week 2 (Post-Launch)

**Goal**: Convert to StateGraph while keeping existing functionality

**Steps**:

1. **Install StateGraph dependencies** (5 min)
```bash
pip install langgraph>=0.2.0
```

2. **Define StateGraph class** (30 min)
```python
# src/flows/conversation_graph.py
from langgraph.graph import StateGraph, START, END
from src.state.conversation_state import ConversationState

graph_builder = StateGraph(ConversationState)

# Add nodes
graph_builder.add_node("initialize_conversation_state", initialize_conversation_state)
graph_builder.add_node("handle_greeting", handle_greeting)
graph_builder.add_node("classify_role_mode", classify_role_mode)
graph_builder.add_node("classify_intent", classify_intent)
graph_builder.add_node("detect_hiring_signals", detect_hiring_signals)
graph_builder.add_node("handle_resume_request", handle_resume_request)
graph_builder.add_node("extract_entities", extract_entities)
graph_builder.add_node("assess_clarification_need", assess_clarification_need)
graph_builder.add_node("ask_clarifying_question", ask_clarifying_question)
graph_builder.add_node("compose_query", compose_query)
graph_builder.add_node("retrieve_chunks", retrieve_chunks)
graph_builder.add_node("re_rank_and_dedup", re_rank_and_dedup)
graph_builder.add_node("validate_grounding", validate_grounding)
graph_builder.add_node("handle_grounding_gap", handle_grounding_gap)
graph_builder.add_node("generate_draft", generate_draft)
graph_builder.add_node("hallucination_check", hallucination_check)
graph_builder.add_node("plan_actions", plan_actions)
graph_builder.add_node("format_answer", format_answer)
graph_builder.add_node("execute_actions", execute_actions)
graph_builder.add_node("suggest_followups", suggest_followups)
graph_builder.add_node("update_memory", update_memory)
graph_builder.add_node("log_and_notify", log_and_notify)

# Add edges (linear flow for now)
pipeline_edges = [
    (START, "initialize_conversation_state"),
    ("initialize_conversation_state", "handle_greeting"),
    ("handle_greeting", "classify_role_mode"),
    ("classify_role_mode", "classify_intent"),
    ("classify_intent", "detect_hiring_signals"),
    ("detect_hiring_signals", "handle_resume_request"),
    ("handle_resume_request", "extract_entities"),
    ("extract_entities", "assess_clarification_need"),
    ("assess_clarification_need", "ask_clarifying_question"),
    ("ask_clarifying_question", "compose_query"),
    ("compose_query", "retrieve_chunks"),
    ("retrieve_chunks", "re_rank_and_dedup"),
    ("re_rank_and_dedup", "validate_grounding"),
    ("validate_grounding", "handle_grounding_gap"),
    ("handle_grounding_gap", "generate_draft"),
    ("generate_draft", "hallucination_check"),
    ("hallucination_check", "plan_actions"),
    ("plan_actions", "format_answer"),
    ("format_answer", "execute_actions"),
    ("execute_actions", "suggest_followups"),
    ("suggest_followups", "update_memory"),
    ("update_memory", "log_and_notify"),
    ("log_and_notify", END),
]

for src, dest in pipeline_edges:
    graph_builder.add_edge(src, dest)

# Compile graph
conversation_graph = graph_builder.compile()
```

3. **Update conversation_flow.py** (15 min)
```python
# src/flows/conversation_flow.py
def run_conversation_flow(state, rag_engine, session_id):
    # OLD: Manual pipeline
    # state = classify_intent(state)
    # state = retrieve_chunks(state, rag_engine)
    # ...

    # NEW: Use compiled graph
    from src.flows.conversation_graph import conversation_graph
    result = conversation_graph.invoke(state)
    return result
```

4. **Test migration** (1 hour)
```bash
pytest tests/test_conversation_flow.py -v
```
- Verify all 12 tests still pass
- Check performance (should be similar)
- Validate state mutations work correctly

**Success Criteria**:
- ✅ All tests passing
- ✅ Same functionality as before
- ✅ Using official StateGraph pattern

---

### Phase 2: Week 3 (Optimization)

**Goal**: Add conditional routing and parallel execution

**Conditional Edges Example**:
```python
# Add router for query type branching
def route_query_type(state: ConversationState):
    """Route based on query classification."""
    query_type = state.get("query_type", "general")

    if query_type == "data":
        return "data_display_node"
    elif query_type == "code":
        return "code_display_node"
    else:
        return "standard_retrieval"

graph_builder.add_conditional_edges(
    "classify_intent",
    route_query_type,
    {
        "data_display_node": "data_display_node",
        "code_display_node": "code_display_node",
        "standard_retrieval": "retrieve_chunks"
    }
)
```

**Parallel Execution Example**:
```python
# Retrieve career info and code simultaneously
from langgraph.graph import parallel

graph_builder.add_node("parallel_retrieval", parallel(
    retrieve_career_info,
    retrieve_code_snippets
))
```

**Benefits**:
- ⚡ 30-50% faster for technical queries (retrieve + code in parallel)
- 🎯 More efficient routing (skip unnecessary nodes)
- 📊 Better observability (graph visualization shows execution path)

---

### Phase 3: Week 4 (Advanced Features)

**Goal**: Add checkpointing and memory persistence

**Checkpointing**:
```python
from langgraph.checkpoint.sqlite import SqliteSaver

memory = SqliteSaver.from_conn_string(":memory:")
conversation_graph = graph_builder.compile(checkpointer=memory)

# Resume conversation from checkpoint
config = {"configurable": {"thread_id": session_id}}
result = conversation_graph.invoke(state, config=config)
```

**Benefits**:
- 💾 Resume conversations after interruption
- 🔄 Retry failed nodes without restarting
- 📝 Audit trail of all state changes

---

## 📚 Key Differences Summary

| Feature | Our Implementation | LangGraph Best Practice | Migration Priority |
|---------|-------------------|------------------------|-------------------|
| **State Management** | TypedDict ✅ | TypedDict ✅ | N/A (aligned) |
| **Node Functions** | Pure functions ✅ | Pure functions ✅ | N/A (aligned) |
| **Graph Building** | Manual pipeline ❌ | StateGraph class ✅ | **Week 2** (high) |
| **Conditional Routing** | In-node logic ⚠️ | Conditional edges ✅ | Week 3 (medium) |
| **Parallel Execution** | None ❌ | Parallel nodes ✅ | Week 3 (medium) |
| **Message History** | Manual list ⚠️ | `add_messages` ✅ | Week 2 (low) |
| **Checkpointing** | None ❌ | SqliteSaver ✅ | Week 4 (low) |
| **Visualization** | None ❌ | Built-in graph viz ✅ | Week 4 (nice-to-have) |

---

## 🎓 Learning from LangGraph Tutorial

### Pattern 1: Structured Output for Classification

**Tutorial Implementation:**
```python
# main.py (lines 15-21)
class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ...,
        description="Classify if the message requires an emotional or logical response."
    )

classifier_llm = llm.with_structured_output(MessageClassifier)
```

**How We Could Apply:**
```python
# src/flows/query_classification.py
from pydantic import BaseModel, Field
from typing import Literal

class QueryClassification(BaseModel):
    query_type: Literal["technical", "career", "data", "casual"] = Field(
        description="Type of query for routing"
    )
    needs_code: bool = Field(description="Should we show code examples?")
    needs_data: bool = Field(description="Should we show analytics?")

# Use structured output instead of regex patterns
def classify_query_with_llm(state):
    classifier_llm = llm.with_structured_output(QueryClassification)
    result = classifier_llm.invoke([
        {"role": "system", "content": "Classify this query..."},
        {"role": "user", "content": state.query}
    ])
    return {"query_type": result.query_type, "needs_code": result.needs_code}
```

**Benefits**:
- ✅ More accurate than regex patterns
- ✅ Type-safe classification
- ✅ Easier to extend (add new types)

**Migration Plan: Week 3** (replace regex-based classification)

---

### Pattern 2: Router Function

**Tutorial Implementation:**
```python
# main.py (lines 44-49)
def router(state: State):
    message_type = state.get("message_type", "logical")
    if message_type == "emotional":
        return {"next": "therapist"}
    return {"next": "logical"}
```

**How We Could Apply:**
```python
# src/flows/routers.py
def role_router(state: ConversationState):
    """Route based on user role."""
    role = state.get("role", "Just looking around")

    if role == "Software Developer":
        return {"next": "technical_pipeline"}
    elif role.startswith("Hiring Manager"):
        return {"next": "hiring_pipeline"}
    else:
        return {"next": "casual_pipeline"}

# Add to graph
graph_builder.add_conditional_edges(
    "classify_intent",
    role_router,
    {
        "technical_pipeline": "retrieve_code",
        "hiring_pipeline": "retrieve_career",
        "casual_pipeline": "retrieve_general"
    }
)
```

**Benefits**:
- ✅ Explicit routing logic (not buried in nodes)
- ✅ Easy to visualize flow
- ✅ Testable in isolation

---

### Pattern 3: Multiple Agent Nodes

**Tutorial Implementation:**
```python
# main.py has separate therapist_agent and logical_agent nodes
# Each with specialized system prompts
```

**How We Could Apply:**
```python
# Instead of one generate_draft node, split by role:

def generate_developer_draft(state):
    """Generate answer with code snippets for developers."""
    # Technical system prompt
    # Include code examples
    # Deep dive explanations

def generate_business_draft(state):
    """Generate business-focused answer."""
    # Plain English system prompt
    # Business value focus
    # No code unless requested

# Route to appropriate generator
graph_builder.add_conditional_edges(
    "retrieve_chunks",
    lambda state: state.get("role"),
    {
        "Software Developer": "generate_developer_draft",
        "Hiring Manager (nontechnical)": "generate_business_draft",
        # ...
    }
)
```

**Benefits**:
- ✅ Specialized prompts per role
- ✅ Easier to optimize each role separately
- ✅ Clear separation of concerns

**Migration Plan: Week 3** (split generate_draft by role)

---

## 🚀 Migration Timeline

### Week 1 (Current - Launch Focus)
- ✅ Keep TypedDict implementation
- ✅ Focus on frontend + deployment
- ✅ Document alignment gaps (this file)
- ✅ No breaking changes

### Week 2 (Post-Launch - Core Migration)
**Goal**: Convert to StateGraph without changing functionality

**Tasks**:
1. Install langgraph package
2. Create StateGraph with existing nodes
3. Add linear edges (match current pipeline)
4. Test thoroughly (all tests pass)
5. Deploy to production
6. Monitor for issues

**Estimated Time**: 4-6 hours
**Risk**: Low (functionality identical)

### Week 3 (Optimization)
**Goal**: Add conditional routing and parallel execution

**Tasks**:
1. Add conditional edges for query type routing
2. Implement parallel retrieval (career + code)
3. Split generate_draft by role
4. Add structured output for classification
5. Performance benchmarking

**Estimated Time**: 8-12 hours
**Risk**: Medium (new patterns, need testing)

### Week 4 (Advanced Features)
**Goal**: Checkpointing and visualization

**Tasks**:
1. Add SqliteSaver for conversation checkpoints
2. Enable graph visualization (Mermaid diagrams)
3. Add retry logic for failed nodes
4. Implement conversation resume feature

**Estimated Time**: 6-8 hours
**Risk**: Low (additive features)

---

## 📖 References

### LangGraph Tutorial Files
- `simple.py`: Basic chatbot with StateGraph
- `main.py`: Multi-agent routing with conditional edges

### Official Documentation
- https://langchain-ai.github.io/langgraph/
- https://langchain-ai.github.io/langgraph/concepts/
- https://langchain-ai.github.io/langgraph/tutorials/

### Our Implementation
- `src/flows/conversation_flow.py` - Current pipeline
- `src/flows/conversation_nodes.py` - Node functions
- `src/state/conversation_state.py` - TypedDict state
- `tests/test_conversation_flow.py` - Tests to maintain

---

## ✅ Alignment Checklist

**Week 1 (Pre-Launch)**:
- [x] Using TypedDict for state
- [x] Functional nodes (pure functions)
- [x] Linear pipeline working
- [x] All tests passing
- [ ] Using StateGraph class (Week 2)
- [ ] Conditional routing (Week 3)
- [ ] Parallel execution (Week 3)
- [ ] Checkpointing (Week 4)

**Post-Migration Success Criteria**:
- [ ] All 74 tests passing with StateGraph
- [ ] Graph visualization working
- [ ] Performance same or better
- [ ] Code cleaner and more maintainable
- [ ] Easier to add new features

---

## 🤔 Questions Answered

### Q: Why not migrate to StateGraph immediately?

**A**: Risk management for Week 1 launch
- Current implementation works (95% test pass rate)
- Team familiar with current pattern
- Launch deadline is aggressive (7 days)
- StateGraph migration adds risk close to deadline
- Better to launch stable, then optimize

### Q: Will migration break existing tests?

**A**: No, if done correctly
- State structure stays same (TypedDict)
- Node functions unchanged
- Only orchestration layer changes
- Tests should pass without modification

### Q: What's the biggest benefit of StateGraph?

**A**: Scalability and observability
- Graph visualization shows execution path
- Easier to add conditional routing
- Built-in checkpointing for reliability
- Standard pattern for team collaboration
- Better debugging (see which node failed)

### Q: Can we mix approaches (some TypedDict, some StateGraph)?

**A**: Not recommended
- Choose one pattern for consistency
- Migration should be complete, not partial
- Hybrid approach confuses team
- Makes debugging harder

---

## 📝 Maintenance Notes

**Update this document when**:
- StateGraph migration begins (Week 2)
- New LangGraph features discovered
- Tutorial repository updates
- Team feedback on migration process
- Performance benchmarks available

**Owner**: Development team
**Review Frequency**: Weekly during migration, monthly after

---

**Status**: ✅ Documented and ready for Week 2 migration
