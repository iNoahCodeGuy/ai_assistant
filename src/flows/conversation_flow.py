"""Lightweight orchestrator to emulate a LangGraph conversation flow."""

from __future__ import annotations

import time
from typing import Callable

from src.core.rag_engine import RagEngine
from src.flows.conversation_state import ConversationState
from src.flows.conversation_nodes import (
    classify_query,
    retrieve_chunks,
    generate_answer,
    plan_actions,
    apply_role_context,
    execute_actions,
    log_and_notify,
)


Node = Callable[[ConversationState], ConversationState]


def run_conversation_flow(
    state: ConversationState,
    rag_engine: RagEngine,
    *,
    nodes: tuple[Node, ...] | None = None,
    session_id: str,
) -> ConversationState:
    """Execute the conversation pipeline in sequence."""
    pipeline = nodes or (
        classify_query,
        lambda s: retrieve_chunks(s, rag_engine),
        lambda s: generate_answer(s, rag_engine),
        plan_actions,
        lambda s: apply_role_context(s, rag_engine),
        execute_actions,
    )

    start = time.time()
    for node in pipeline:
        state = node(state)

    elapsed_ms = int((time.time() - start) * 1000)
    state = log_and_notify(state, session_id=session_id, latency_ms=elapsed_ms)
    return state
