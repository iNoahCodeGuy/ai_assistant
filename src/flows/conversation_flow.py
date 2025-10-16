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
    handle_greeting,
)


Node = Callable[[ConversationState], ConversationState]


def run_conversation_flow(
    state: ConversationState,
    rag_engine: RagEngine,
    *,
    nodes: tuple[Node, ...] | None = None,
    session_id: str,
) -> ConversationState:
    """Execute the conversation pipeline in sequence.

    Flow: handle_greeting → classify → retrieve → generate → plan → apply → execute → log

    The greeting node short-circuits if user's first query is a simple "hello".
    """
    pipeline = nodes or (
        lambda s: handle_greeting(s, rag_engine),  # Check for first-turn greetings
        classify_query,
        lambda s: retrieve_chunks(s, rag_engine) if not s.fetch("is_greeting") else s,
        lambda s: generate_answer(s, rag_engine) if not s.fetch("is_greeting") else s,
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
