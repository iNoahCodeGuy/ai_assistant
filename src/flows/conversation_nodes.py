"""Conversation nodes orchestrator - imports modular functions.

This module acts as the central import point for all conversation pipeline nodes.
The actual implementations live in focused modules:

- query_classification.py: classify_query() - intent detection
- core_nodes.py: retrieve_chunks, generate_answer, apply_role_context, log_and_notify
- action_planning.py: plan_actions() - build action shopping list
- action_execution.py: execute_actions() - perform side effects
- code_validation.py: is_valid_code_snippet, sanitize_generated_answer

For junior developers: This file is now just a convenience wrapper that re-exports
functions from specialized modules. Each module has detailed docstrings explaining
what that part of the pipeline does.

See docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md for the full conversation flow diagram.
"""

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
