"""Compatibility RoleRouter wrapper.

This module keeps the legacy ``RoleRouter`` API available for tests and
example scripts while delegating to the modern LangGraph-aware stack. It
classifies queries with lightweight heuristics, calls into ``RagEngine``
when available, and returns the historical dictionary payload expected by
older integrations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.config.supabase_config import supabase_settings
from src.flows.query_classification import detect_topic_focus

_TECH_KEYWORDS = (
    "code",
    "stack",
    "implementation",
    "deploy",
    "diagram",
    "architecture",
    "langgraph",
    "retrieval",
    "rag",
    "supabase",
    "vector",
)

_CONFESSION_KEYWORDS = ("confess", "crush", "secret", "message for noah")


@dataclass
class Classification:
    query_type: str
    topic_focus: str
    include_code: bool


class RoleRouter:
    """Small compatibility layer for legacy integrations."""

    def __init__(self) -> None:
        self.settings = supabase_settings

    def _classify_query(self, query: str, role: str) -> Classification:
        lowered = (query or "").strip().lower()
        if not lowered:
            return Classification("general", "general", include_code=False)

        if any(token in lowered for token in _CONFESSION_KEYWORDS) or role == "Looking to confess crush":
            return Classification("confession", detect_topic_focus(query), include_code=False)

        topic_focus = detect_topic_focus(query)
        if any(token in lowered for token in _TECH_KEYWORDS):
            include_code = role in {"Software Developer", "Hiring Manager (technical)"}
            return Classification("technical", topic_focus, include_code=include_code)

        if role in {"Hiring Manager (technical)", "Software Developer"}:
            return Classification("technical", topic_focus, include_code=True)

        return Classification("career", topic_focus, include_code=False)

    def route(
        self,
        role: str,
        query: str,
        memory: Any,
        rag_engine: Any,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        classification = self._classify_query(query, role)
        if hasattr(memory, "set_role"):
            memory.set_role(role)

        if classification.query_type == "confession":
            message = (
                "💌 I can pass that along discreetly. Share whatever you'd like—"
                "I'll keep it private unless you ask me to introduce you."
            )
            return {
                "type": "confession",
                "topic_focus": classification.topic_focus,
                "response": message,
            }

        response_text = "Let me gather the highlights."
        context: Dict[str, Any] = {
            "type": classification.query_type,
            "topic_focus": classification.topic_focus,
        }

        generator = getattr(rag_engine, "generate_response", None)
        if callable(generator):
            try:
                response_text = generator(query, chat_history=chat_history)
            except TypeError:
                response_text = generator(query)

        if classification.query_type == "technical":
            include_code = classification.include_code
            retrieve_with_code = getattr(rag_engine, "retrieve_with_code", None)
            code_payload = None
            if callable(retrieve_with_code):
                try:
                    code_payload = retrieve_with_code(query, role=role, include_code=include_code)
                except TypeError:
                    code_payload = retrieve_with_code(query, role=role)
            elif include_code:
                code_info = getattr(rag_engine, "retrieve_code_info", None)
                if callable(code_info):
                    code_payload = code_info(query, role=role)
            if code_payload:
                context["code"] = code_payload
        else:
            career_retrieve = getattr(rag_engine, "retrieve_career_info", None)
            if callable(career_retrieve):
                context["career_matches"] = career_retrieve(query, role=role)

        context["response"] = response_text
        return context


__all__ = ["RoleRouter"]
