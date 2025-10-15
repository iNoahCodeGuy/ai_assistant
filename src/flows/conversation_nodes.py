"""Conversation nodes orchestrator - imports modular functions.

This module acts as the central import point for all conversation pipeline nodes.
All node logic has been extracted into focused modules for maintainability:

- query_classification.py: Intent detection and routing
- core_nodes.py: Retrieval, generation, and logging
- action_planning.py: Role-based action generation
- action_execution.py: Side effects (email, SMS, storage)
- code_validation.py: Sanitization and validation utilities
- greetings.py: Role-specific welcome messages

Each module is <200 lines and handles a single responsibility.
This file simply re-exports the functions so callers can import from one place.

See docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md for the full conversation flow diagram.
See docs/CONVERSATION_PIPELINE_MODULES.md for implementation details.
"""

# Import all conversation nodes from their focused modules
from src.flows.query_classification import classify_query
from src.flows.core_nodes import retrieve_chunks, generate_answer, apply_role_context, log_and_notify
from src.flows.action_planning import plan_actions
from src.flows.action_execution import execute_actions
from src.flows.greetings import get_role_greeting, should_show_greeting, is_first_turn


def handle_greeting(state, rag_engine):
    """Check if this is a first-turn greeting and respond appropriately.
    
    If the user's first query is a simple greeting (hi/hello/hey), we respond
    with a warm, role-specific introduction per CONVERSATION_PERSONALITY.md.
    
    Args:
        state: ConversationState with query and role
        rag_engine: RAG engine (not used for greetings, but part of node signature)
        
    Returns:
        Updated state with greeting as answer, or unchanged if not a greeting
    """
    if should_show_greeting(state.query, state.chat_history):
        greeting = get_role_greeting(state.role)
        state.set_answer(greeting)
        state.stash("is_greeting", True)
    return state


# Export all nodes for use in conversation_flow.py
__all__ = [
    "classify_query",
    "retrieve_chunks", 
    "generate_answer",
    "apply_role_context",
    "log_and_notify",
    "plan_actions",
    "execute_actions",
    "handle_greeting",
    "get_role_greeting",
    "is_first_turn",
]

from __future__ import annotations

# Import all conversation nodes from their focused modules
from src.flows.query_classification import classify_query
from src.flows.core_nodes import (
    retrieve_chunks,
    generate_answer,
    apply_role_context,
    log_and_notify
)
from src.flows.action_planning import plan_actions
from src.flows.action_execution import execute_actions
from src.flows.code_validation import (
    is_valid_code_snippet,
    sanitize_generated_answer
)

# Re-export everything so existing code doesn't break
__all__ = [
    "classify_query",
    "retrieve_chunks",
    "generate_answer",
    "plan_actions",
    "apply_role_context",
    "execute_actions",
    "log_and_notify",
    "is_valid_code_snippet",
    "sanitize_generated_answer",
]
