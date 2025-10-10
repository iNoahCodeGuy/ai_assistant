from typing import Dict, Any, List, Optional
from src.core.rag_engine import RagEngine
from src.core.memory import Memory
from src.config.supabase_config import supabase_settings
from .roles import role_include_code  # NEW import

class RoleRouter:
    """Routes queries based on user role and query type."""

    def __init__(self):
        self.settings = supabase_settings

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
            return self._handle_hiring_manager(query, query_type, rag_engine, technical=False, chat_history=chat_history)
        if role == "Hiring Manager (technical)":
            return self._handle_hiring_manager(query, query_type, rag_engine, technical=True, chat_history=chat_history)
        if role == "Software Developer":
            return self._handle_developer(query, query_type, rag_engine, chat_history=chat_history)
        if role == "Just looking around":
            return self._handle_casual(query, query_type, rag_engine, chat_history=chat_history)
        if role == "Looking to confess crush":
            return self._handle_confession(query)
        return {"response": "Please select a valid role to continue.", "type": "error", "context": []}

    def _classify_query(self, query: str) -> str:
        q = query.lower()
        # Check for specific MMA keywords (use word boundaries to avoid false matches)
        import re
        if any(re.search(r'\b' + k + r'\b', q) for k in ["mma", "fight", "ufc", "bout", "cage"]):
            return "mma"
        # Check for fun fact requests (be more specific)
        if any(k in q for k in ["fun fact", "hobby", "hobbies", "interesting fact"]):
            return "fun"
        # Check for technical queries
        if any(k in q for k in ["code", "technical", "stack", "function", "architecture", "retrieval", "implementation"]):
            return "technical"
        # Check for career queries
        if any(k in q for k in ["career", "resume", "cv", "experience", "achievement", "role history", "work"]):
            return "career"
        return "general"

    def _handle_hiring_manager(self, query: str, query_type: str, rag_engine: RagEngine, technical: bool, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        # Check if this is a "show me" or "display" query - return raw content
        if any(keyword in query.lower() for keyword in ["show me", "display", "show the", "diagram", "code example"]):
            ctx = rag_engine.retrieve(query)
            # Get the best match and return its content directly
            if ctx and ctx.get("chunks"):
                best_chunk = ctx["chunks"][0]
                # Extract the answer part (after "Answer: ")
                content = best_chunk.get('content', '')
                if "Answer: " in content:
                    resp = content.split("Answer: ", 1)[1]
                else:
                    resp = content
                # Return with full chunks for source citations
                return {"response": resp, "type": "technical", "context": ctx.get("chunks", [])}
        
        if technical and query_type == "technical":
            ctx = rag_engine.retrieve(query)
            resp = self._handle_technical_manager(query, ctx, rag_engine, chat_history)
            return {"response": resp, "type": "technical", "context": ctx.get("chunks", [])}
        # Default to career-focused for nontechnical or non-technical query
        ctx = rag_engine.retrieve(query)
        resp = rag_engine.generate_response(query, chat_history=chat_history)
        return {"response": resp, "type": "career", "context": ctx.get("chunks", [])}

    def _handle_technical_manager(self, user_input: str, context: str, rag_engine: RagEngine, chat_history: List[Dict[str, str]] = None) -> str:
        """Enhanced technical manager handling with code snippets."""
        include_code = True  # technical manager always gets code for technical queries
        results = rag_engine.retrieve_with_code(user_input, role="Hiring Manager (technical)")
        
        # Use basic generate_response method with chat history
        response = rag_engine.generate_response(user_input, chat_history=chat_history)
        
        # Add code snippets to response
        if results.get("code_snippets"):
            response += "\n\n**Code References:**\n"
            for snippet in results["code_snippets"]:
                response += f"- [{snippet['citation']}]({snippet['github_url']})\n"
        
        return response

    def _handle_developer(self, query: str, query_type: str, rag_engine: RagEngine, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        # Check if this is a "show me" or "display" query - return raw content
        if any(keyword in query.lower() for keyword in ["show me", "display", "show the", "diagram", "code example", "file structure"]):
            ctx = rag_engine.retrieve(query)
            # Get the best match and return its content directly
            if ctx and ctx.get("chunks"):
                best_chunk = ctx["chunks"][0]
                # Extract the answer part (after "Answer: ")
                content = best_chunk.get('content', '')
                if "Answer: " in content:
                    resp = content.split("Answer: ", 1)[1]
                else:
                    resp = content
                # Return with full chunks for source citations
                return {"response": resp, "type": "technical", "context": ctx.get("chunks", [])}
        
        if query_type == "technical":
            ctx = rag_engine.retrieve(query)
            resp = self._handle_developer_with_code(query, ctx, rag_engine, chat_history)
            return {"response": resp, "type": "technical", "context": ctx.get("chunks", [])}
        ctx = rag_engine.retrieve(query)
        resp = rag_engine.generate_response(query, chat_history=chat_history)
        return {"response": resp, "type": query_type, "context": ctx.get("chunks", [])}

    def _handle_developer_with_code(self, user_input: str, context: str, rag_engine: RagEngine, chat_history: List[Dict[str, str]] = None) -> str:
        """Enhanced developer handling with detailed code integration."""
        include_code = True
        results = rag_engine.retrieve_with_code(user_input, role="Software Developer")
        
        # Use basic generate_response method with chat history
        response = rag_engine.generate_response(user_input, chat_history=chat_history)
        
        if results.get("code_snippets"):
            response += "\n\n## Code Implementation\n"
            for snippet in results["code_snippets"]:
                response += f"\n### {snippet['name']} ([{snippet['citation']}]({snippet['github_url']}))\n"
                response += f"```python\n{snippet['content']}\n```\n"
        
        return response

    def _handle_casual(self, query: str, query_type: str, rag_engine: RagEngine, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        if query_type == "mma":
            return {
                "response": "Noah's MMA fight link:",
                "type": "mma",
                "youtube_link": self.settings.youtube_fight_link
            }
        if query_type == "fun":
            # Temporary reuse of career KB – replace with dedicated fun facts store later
            ctx = rag_engine.retrieve("fun facts about Noah")
            synthesized = rag_engine.generate_response("List 3 short fun facts about Noah. Keep total under 60 words.", chat_history=chat_history)
            return {"response": synthesized, "type": "fun", "context": ctx}
        ctx = rag_engine.retrieve(query)
        resp = rag_engine.generate_response(query, chat_history=chat_history)
        return {"response": resp, "type": "general", "context": ctx}

    def _handle_confession(self, query: str) -> Dict[str, Any]:
        # No retrieval or LLM call for privacy / simplicity
        return {
            "response": "Your message is noted. Use the form below to submit confessions. 💌",
            "type": "confession",
            "context": []  # ← Add empty context to prevent formatter errors
        }