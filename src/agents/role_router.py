from typing import List, Dict, Any, Optional
from core.memory import Memory
from core.rag_engine import RagEngine

class RoleRouter:
    def __init__(self, max_context_tokens: int = 4000):
        self.max_context_tokens = max_context_tokens
        
    def route(
        self, 
        role: str, 
        user_input: str, 
        memory: Memory, 
        rag_engine: RagEngine,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Route user input based on role with chat history context."""
        
        # Truncate chat history if needed
        truncated_history = self._truncate_chat_history(chat_history or [])
        
        # Build context from history
        context = self._build_context_from_history(truncated_history)
        
        # Route based on role
        if role == "Hiring Manager (nontechnical)":
            return self._handle_nontechnical_manager(user_input, context, rag_engine)
        elif role == "Hiring Manager (technical)":
            return self._handle_technical_manager(user_input, context, rag_engine)
        elif role == "Software Developer":
            return self._handle_developer(user_input, context, rag_engine)
        elif role == "Just looking around":
            return self._handle_casual(user_input, context, rag_engine)
        elif role == "Looking to confess crush":
            return self._handle_confession(user_input, context)
        else:
            return self._handle_default(user_input, context, rag_engine)
    
    def _truncate_chat_history(self, chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Keep recent messages within token budget."""
        if not chat_history:
            return []
            
        # Rough token estimation: 4 chars = 1 token
        current_tokens = 0
        truncated = []
        
        # Work backwards from most recent
        for message in reversed(chat_history[-20:]):  # Max 20 recent messages
            message_tokens = len(message.get("content", "")) // 4
            if current_tokens + message_tokens > self.max_context_tokens:
                break
            truncated.insert(0, message)
            current_tokens += message_tokens
            
        return truncated
    
    def _build_context_from_history(self, chat_history: List[Dict[str, str]]) -> str:
        """Build context string from chat history."""
        if not chat_history:
            return ""
            
        context_parts = ["Previous conversation:"]
        for msg in chat_history[-6:]:  # Last 6 messages for context
            role = "Human" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def _handle_nontechnical_manager(self, user_input: str, context: str, rag_engine: RagEngine) -> str:
        """Handle nontechnical hiring manager queries."""
        return f"Based on Noah's background and the query '{user_input}', here's what you should know about his qualifications and experience."
    
    def _handle_technical_manager(self, user_input: str, context: str, rag_engine: RagEngine) -> str:
        """Handle technical hiring manager queries."""
        return f"Technical response for '{user_input}' with detailed analysis of Noah's technical capabilities."
    
    def _handle_developer(self, user_input: str, context: str, rag_engine: RagEngine) -> str:
        """Handle software developer queries."""
        return f"Developer-focused response for '{user_input}' with code examples and technical depth."
    
    def _handle_casual(self, user_input: str, context: str, rag_engine: RagEngine) -> str:
        """Handle casual visitor queries."""
        return f"Friendly response about Noah's background for '{user_input}' including interesting details."
    
    def _handle_confession(self, user_input: str, context: str) -> str:
        """Handle confession queries with appropriate boundaries."""
        return "Thank you for sharing! While I appreciate your message, I'm focused on helping visitors learn about Noah's professional background and projects."
    
    def _handle_default(self, user_input: str, context: str, rag_engine: RagEngine) -> str:
        """Default handler for unspecified roles."""
        return f"General response about Noah's background for '{user_input}'."