from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from core.memory import Memory
from core.rag_engine import RagEngine

router = APIRouter()

class UserQuery(BaseModel):
    role: str
    query: str

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
        prompt = f"""
        {context}
        
        Current question: {user_input}
        
        Provide a professional, business-focused response about Noah's career and qualifications.
        Focus on achievements, skills, and cultural fit. Avoid technical jargon.
        """
        
        relevant_docs = rag_engine.retrieve(user_input, top_k=3)
        return rag_engine.generate_response(prompt, relevant_docs)
    
    def _handle_technical_manager(self, user_input: str, context: str, rag_engine: RagEngine) -> str:
        """Handle technical hiring manager queries."""
        prompt = f"""
        {context}
        
        Current question: {user_input}
        
        Provide a detailed technical response about Noah's skills and projects.
        Include specific technologies, code examples, and technical achievements.
        Format response with both technical details and plain-English summary.
        """
        
        relevant_docs = rag_engine.retrieve(user_input, top_k=5)
        return rag_engine.generate_response(prompt, relevant_docs)
    
    def _handle_developer(self, user_input: str, context: str, rag_engine: RagEngine) -> str:
        """Handle software developer queries."""
        prompt = f"""
        {context}
        
        Current question: {user_input}
        
        Provide a peer-to-peer technical response with code examples, 
        architecture details, and implementation specifics about Noah's work.
        Include citations to specific files and line numbers where relevant.
        """
        
        relevant_docs = rag_engine.retrieve(user_input, top_k=7)
        return rag_engine.generate_response(prompt, relevant_docs)
    
    def _handle_casual(self, user_input: str, context: str, rag_engine: RagEngine) -> str:
        """Handle casual visitor queries."""
        prompt = f"""
        {context}
        
        Current question: {user_input}
        
        Provide a friendly, conversational response. Include fun facts about Noah's 
        MMA career, hobbies, or interesting background details. Keep it engaging and light.
        """
        
        relevant_docs = rag_engine.retrieve(user_input, top_k=3)
        return rag_engine.generate_response(prompt, relevant_docs)
    
    def _handle_confession(self, user_input: str, context: str) -> str:
        """Handle confession queries with appropriate boundaries."""
        return """
        Thank you for sharing! While I appreciate your message, I'm focused on 
        helping visitors learn about Noah's professional background and projects. 
        
        If you'd like to connect professionally, you can reach Noah on LinkedIn 
        or GitHub. For other inquiries, please use appropriate channels.
        """
    
    def _handle_default(self, user_input: str, context: str, rag_engine: RagEngine) -> str:
        """Default handler for unspecified roles."""
        relevant_docs = rag_engine.retrieve(user_input, top_k=3)
        prompt = f"""
        {context}
        
        Current question: {user_input}
        
        Provide a helpful response about Noah's background and qualifications.
        """
        
        return rag_engine.generate_response(prompt, relevant_docs)

@router.post("/route_query")
async def route_query(user_query: UserQuery) -> Dict[str, Any]:
    role = user_query.role.lower()
    query = user_query.query

    if role == "hiring manager (nontechnical)":
        return await handle_nontechnical_hiring_manager(query)
    elif role == "hiring manager (technical)":
        return await handle_technical_hiring_manager(query)
    elif role == "software developer":
        return await handle_software_developer(query)
    elif role == "just looking around":
        return await handle_casual_visitor(query)
    elif role == "looking to confess crush":
        return await handle_crush_confession(query)
    else:
        raise HTTPException(status_code=400, detail="Invalid role specified.")

async def handle_nontechnical_hiring_manager(query: str) -> Dict[str, Any]:
    # Logic for handling nontechnical hiring manager queries
    pass

async def handle_technical_hiring_manager(query: str) -> Dict[str, Any]:
    # Logic for handling technical hiring manager queries
    pass

async def handle_software_developer(query: str) -> Dict[str, Any]:
    # Logic for handling software developer queries
    pass

async def handle_casual_visitor(query: str) -> Dict[str, Any]:
    # Logic for handling casual visitor queries
    pass

async def handle_crush_confession(query: str) -> Dict[str, Any]:
    # Logic for handling crush confessions
    pass