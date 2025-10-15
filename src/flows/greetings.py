"""Greeting generators for role-specific welcome messages.

This module implements the conversation personality defined in
docs/context/CONVERSATION_PERSONALITY.md. Each role gets a warm,
enthusiastic greeting that invites exploration and questions.

Usage:
    from src/flows.greetings import get_role_greeting
    
    greeting = get_role_greeting("Software Developer")
    # Returns personalized welcome message
"""

from typing import Dict


def get_role_greeting(role: str) -> str:
    """Get an enthusiastic, role-appropriate greeting.
    
    Implements the personality guidance from CONVERSATION_PERSONALITY.md:
    - Warm and genuinely excited
    - Offers conversation starters tailored to role
    - Invites questions about how the assistant works
    - Balances friendliness with professionalism
    
    Args:
        role: User's selected role (e.g., "Software Developer")
        
    Returns:
        Personalized greeting string with conversation menu
    """
    greetings: Dict[str, str] = {
        "Hiring Manager (technical)": _technical_hiring_manager_greeting(),
        "Hiring Manager (nontechnical)": _nontechnical_hiring_manager_greeting(),
        "Software Developer": _software_developer_greeting(),
        "Just looking around": _casual_visitor_greeting(),
        "Looking to confess crush": _confession_greeting(),
    }
    
    # Return role-specific greeting, or default if role not recognized
    return greetings.get(role, _default_greeting())


def _technical_hiring_manager_greeting() -> str:
    """Greeting for technical hiring managers."""
    return """Hey! 👋 I'm really excited you're here. I'm Noah's AI Assistant, and I want you to understand how generative AI applications like this work and why they're valuable to enterprises.

I can walk you through:
- How RAG (Retrieval-Augmented Generation) ensures accuracy and grounding
- The vector search and semantic retrieval architecture
- LLM orchestration patterns and why they matter for production systems
- Data governance, cost optimization, and reliability strategies
- Why enterprises are investing in GenAI capabilities like this
- How this demonstrates Noah's understanding of production GenAI systems

I'm happy to explain the engineering, the business value, or both. I want you to really *get* why these systems matter. What sounds interesting?"""


def _nontechnical_hiring_manager_greeting() -> str:
    """Greeting for nontechnical hiring managers."""
    return """Hello! 👋 I'm so glad you're here. I'm Noah's AI Assistant, and I want you to understand how generative AI applications like this work and why they're valuable to enterprises — in plain English, no jargon.

I can explain:
- What makes AI assistants like me reliable and accurate (RAG technology)
- Why enterprises are investing in generative AI capabilities
- The business value: cost savings, scalability, and competitive advantage
- How systems like this improve customer experience and operational efficiency
- What Noah understands about building production-ready GenAI applications

I'm here to make GenAI concepts approachable and show you why this technology matters for business. What would be most helpful for you?"""


def _software_developer_greeting() -> str:
    """Greeting for software developers."""
    return """Hey! 👋 So glad you're checking this out. I'm Noah's AI Assistant, and I want you to understand how generative AI applications like this work — not just the surface-level stuff, but the real RAG architecture, vector search, LLM orchestration, and why enterprises care.

Want to explore:
- How RAG (Retrieval-Augmented Generation) works under the hood?
- The vector embedding and semantic search strategy?
- LLM orchestration with LangGraph nodes?
- Prompt engineering and grounding techniques?
- System architecture and why we made specific GenAI tradeoffs?

Or ask me anything about how generative AI applications work — teaching this stuff is what I'm here for. What catches your interest?"""


def _casual_visitor_greeting() -> str:
    """Greeting for casual visitors exploring the assistant."""
    return """Hey there! 👋 Welcome! I'm Noah's AI Assistant, and I'm really happy you stopped by.

I want you to understand how generative AI applications like this work — the cool thing is, it's actually pretty interesting once you see how it works! I'll explain it in plain English, no technical jargon required.

Feel free to ask me:
- How do AI assistants like me actually work?
- What makes me accurate vs just making stuff up?
- How do I remember our conversation?
- Why are companies investing in this technology?
- Anything about Noah's background or this project!

What would you like to explore?"""


def _confession_greeting() -> str:
    """Greeting for confession mode (playful)."""
    return """Hey! 👋 I'm Noah's AI Assistant, and I'm here to help with whatever you'd like to share.

This is a fun, judgment-free space. Want to leave a message? I can keep it anonymous or include your name — totally up to you!

Or if you'd rather just chat about something else, that's cool too. What's on your mind?"""


def _default_greeting() -> str:
    """Default greeting for unrecognized roles."""
    return """Hey! 👋 I'm Noah's AI Assistant, and I'm excited you're here.

I want you to understand:
- How generative AI applications like this work
- What makes them valuable to enterprises
- The technology behind AI assistants (RAG, vector search, LLMs)
- Noah's background and this project

I can explain things technically or in plain English — whatever works best for you. And I'm always happy to show you how the GenAI systems work under the hood.

What would you like to explore?"""


def is_first_turn(chat_history: list) -> bool:
    """Check if this is the first turn of the conversation.
    
    Args:
        chat_history: List of conversation messages
        
    Returns:
        True if this is the first user query (no assistant messages yet)
    """
    if not chat_history:
        return True
    
    # Check if there are any assistant messages
    assistant_messages = [msg for msg in chat_history if msg.get("role") == "assistant"]
    return len(assistant_messages) == 0


def should_show_greeting(query: str, chat_history: list) -> bool:
    """Determine if we should show a greeting instead of answering the query.
    
    Show greeting if:
    1. This is the first turn AND
    2. The query is a simple greeting/hello (not a substantive question)
    
    Args:
        query: User's query text
        chat_history: Conversation history
        
    Returns:
        True if we should respond with a greeting
    """
    if not is_first_turn(chat_history):
        return False
    
    # Simple greetings that warrant a warm introduction
    greeting_patterns = [
        "hello", "hi", "hey", "greetings", "good morning", 
        "good afternoon", "good evening", "what's up", "sup",
        "how are you", "how do you do"
    ]
    
    query_lower = query.lower().strip()
    
    # Check if query is primarily a greeting (≤5 words and contains greeting)
    words = query_lower.split()
    if len(words) <= 5:
        for pattern in greeting_patterns:
            if pattern in query_lower:
                return True
    
    return False
