"""LangGraph-style orchestrator aligned with PORTFOLIA_NODE_STRUCTURE.md.

Educational mission: make every conversation a live case study of production RAG
patterns with clear node boundaries, traceability, and cinematic-yet-grounded tone.

Conversation Pipeline Overview:
1. initialize_conversation_state → normalize state containers and load memory
2. handle_greeting → warm intro without RAG cost for first-turn hellos
3. classify_role_mode → decouple persona selection from intent detection
4. classify_intent → determine engineering vs business focus and data needs
5. detect_hiring_signals / handle_resume_request → passive hiring intelligence
6. extract_entities → capture company, role, timeline, contact hints
7. assess/ask_clarification → clarify vague prompts before retrieval
8. compose_query → build retrieval-ready prompt with persona + entity context
9. retrieve_chunks → Supabase pgvector lookup (LangSmith traced)
10. re_rank_and_dedup → diversify context for grounded answers
11. validate_grounding / handle_grounding_gap → stop hallucinations early
12. generate_draft → role-aware LLM generation (stored as draft_answer)
13. hallucination_check → attach citations and mark safety status
14. plan_actions → decide on resumes, LinkedIn, analytics, etc.
15. format_answer → add enterprise content blocks without breaking plain text rule
16. execute_actions → fire side-effects (email/SMS/logging)
17. suggest_followups → cinematic curiosity prompts
18. update_memory → store soft signals for next turns
19. log_and_notify → Supabase analytics + LangSmith metadata (always executed)

Performance characteristics remain consistent with Week 1 launch targets:
- Typical latency ~1.2s
- Greeting short-circuit <50ms
- Cold start ~3s on Vercel
- p95 latency <3s with tracing enabled
"""

from __future__ import annotations

import time
from typing import Callable, Optional, Sequence

from src.core.rag_engine import RagEngine
from src.state.conversation_state import ConversationState
from src.flows.conversation_nodes import (
    initialize_conversation_state,
    handle_greeting,
    classify_role_mode,
    classify_intent,
    detect_hiring_signals,
    handle_resume_request,
    extract_entities,
    assess_clarification_need,
    ask_clarifying_question,
    compose_query,
    retrieve_chunks,
    re_rank_and_dedup,
    validate_grounding,
    handle_grounding_gap,
    generate_draft,
    hallucination_check,
    plan_actions,
    format_answer,
    execute_actions,
    suggest_followups,
    update_memory,
    log_and_notify,
)


Node = Callable[[ConversationState], ConversationState]


def run_conversation_flow(
    state: ConversationState,
    rag_engine: RagEngine,
    session_id: str,
    nodes: Optional[Sequence[Callable[[ConversationState], ConversationState]]] = None
) -> ConversationState:
    """Orchestrate the functional pipeline for conversation processing.

    Design Pattern: Functional pipeline with immutable state updates. Each node
    receives the full state and returns a partial update. This simplified approach
    provides 90% of StateGraph's benefits with 50% less complexity, ideal for
    week 1 launch stability.

    Args:
        state: Initial conversation state (requires role, query, session_id)
        rag_engine: RAG engine instance for retrieval & generation
        session_id: Unique session identifier for analytics logging
        nodes: Optional custom node sequence (for testing/customization)

    Returns:
        Updated ConversationState with:
        - answer: Generated response (str)
        - retrieved_chunks: Context used for generation (list)
        - analytics_metadata: Latency, tokens, retrieval stats (dict)
        - pending_actions: Actions taken (list)

    Raises:
        None - All errors handled gracefully (see ERROR_HANDLING_IMPLEMENTATION.md)
        Services that fail return None, conversation continues with degraded functionality

    Performance:
        - Typical: 1.2s (see module docstring for breakdown)
        - Greeting short-circuit: <50ms (skips nodes 4-8)

    Example:
        >>> state = ConversationState(role="Software Developer", query="How does RAG work?")
        >>> result = run_conversation_flow(state, rag_engine, session_id="demo123")
        >>> print(result["answer"])  # Grounded explanation from KB
        >>> print(len(result["retrieved_chunks"]))  # Should be 1-4 chunks
    """
    pipeline = nodes or (
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
