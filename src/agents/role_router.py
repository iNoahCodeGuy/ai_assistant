from typing import Dict, Any, List, Optional
from core.rag_engine import RagEngine
from core.memory import Memory
from config.settings import Settings

class RoleRouter:
    """Routes queries based on user role and query type."""

    def __init__(self):
        self.settings = Settings()

    def route(
        self,
        role: str,
        query: str,
        memory: Memory,
        rag_engine: RagEngine,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Route query based on role and content.
        chat_history kept optional for future LangGraph or summarization hooks.
        """
        memory.set_role(role)
        query_type = self._classify_query(query)

        if role == "Hiring Manager (nontechnical)":
            return self._handle_hiring_manager(query, query_type, rag_engine, technical=False)
        if role == "Hiring Manager (technical)":
            return self._handle_hiring_manager(query, query_type, rag_engine, technical=True)
        if role == "Software Developer":
            return self._handle_developer(query, query_type, rag_engine)
        if role == "Just looking around":
            return self._handle_casual(query, query_type, rag_engine)
        if role == "Looking to confess crush":
            return self._handle_confession(query)
        return {"response": "Please select a valid role to continue.", "type": "error"}

    def _classify_query(self, query: str) -> str:
        q = query.lower()
        if any(k in q for k in ["mma", "fight", "ufc", "bout"]):
            return "mma"
        if any(k in q for k in ["fun fact", "fun", "fact", "hobby"]):
            return "fun"
        if any(k in q for k in ["code", "technical", "stack", "function", "architecture", "retrieval"]):
            return "technical"
        if any(k in q for k in ["career", "resume", "cv", "experience", "achievement", "role history"]):
            return "career"
        return "general"

    def _handle_hiring_manager(self, query: str, query_type: str, rag_engine: RagEngine, technical: bool) -> Dict[str, Any]:
        if technical and query_type == "technical":
            ctx = rag_engine.retrieve_code_info(query)
            resp = rag_engine.generate_response(query, ctx, "Hiring Manager (technical)")
            return {"response": resp, "type": "technical", "context": ctx}
        # Default to career-focused for nontechnical or non-technical query
        ctx = rag_engine.retrieve_career_info(query)
        resp = rag_engine.generate_response(query, ctx,
                                            "Hiring Manager (technical)" if technical else "Hiring Manager (nontechnical)")
        return {"response": resp, "type": "career", "context": ctx}

    def _handle_developer(self, query: str, query_type: str, rag_engine: RagEngine) -> Dict[str, Any]:
        if query_type == "technical":
            ctx = rag_engine.retrieve_code_info(query)
        else:
            ctx = rag_engine.retrieve_career_info(query)
        resp = rag_engine.generate_response(query, ctx, "Software Developer")
        return {"response": resp, "type": query_type, "context": ctx}

    def _handle_casual(self, query: str, query_type: str, rag_engine: RagEngine) -> Dict[str, Any]:
        if query_type == "mma":
            return {
                "response": "Noah's MMA fight link:",
                "type": "mma",
                "youtube_link": self.settings.youtube_fight_link
            }
        if query_type == "fun":
            # Temporary reuse of career KB – replace with dedicated fun facts store later
            ctx = rag_engine.retrieve_career_info("fun facts about Noah")
            synthesized = rag_engine.generate_response(
                "List 3 short fun facts about Noah. Keep total under 60 words.",
                ctx,
                "Casual Visitor"
            )
            return {"response": synthesized, "type": "fun", "context": ctx}
        ctx = rag_engine.retrieve_career_info(query)
        resp = rag_engine.generate_response(query, ctx, "Casual Visitor")
        return {"response": resp, "type": "general", "context": ctx}

    def _handle_confession(self, query: str) -> Dict[str, Any]:
        # No retrieval or LLM call for privacy / simplicity
        return {
            "response": "Your message is noted. Use the form for new confessions. 💌",
            "type": "confession"
        }