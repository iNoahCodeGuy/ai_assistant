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
    return """Hey! 👋 I'm really excited you're here. I'm Noah's AI Assistant, and I'd love to show you what makes this project interesting from an engineering perspective.

I'm here to help you really understand the architecture and design thinking — think of me as a senior staff engineer walking you through a system design.

I can walk you through:
- How my RAG pipeline works (pgvector + LangGraph orchestration)
- The data contracts and analytics strategy
- How this could scale in an enterprise context
- Design tradeoffs and why we made certain choices
- Noah's technical background and engineering approach

I'm also happy to explain how I was built, dive into specific technical decisions, or show you the code. I want you to understand it, not just see it. What sounds interesting?"""


def _nontechnical_hiring_manager_greeting() -> str:
    """Greeting for nontechnical hiring managers."""
    return """Hello! 👋 I'm so glad you're here. I'm Noah's AI Assistant, and I'd love to help you learn more about Noah's work and capabilities.

I can share:
- Noah's background and experience
- What this project demonstrates
- How it could benefit your organization
- The value of Noah's skill set

I'm also happy to explain how I work in plain English — no jargon required. I can even walk you through my architecture in a way that makes sense from a business perspective.

What would be most helpful for you?"""


def _software_developer_greeting() -> str:
    """Greeting for software developers."""
    return """Hey! 👋 So glad you're checking this out. I'm Noah's AI Assistant, and honestly, I'm kind of excited to geek out with another developer.

I want you to really understand how this system works — not just what it does, but *why* it's built this way. Think of me as that senior staff engineer who loves explaining architecture.

Want to explore:
- Code snippets from the RAG engine or conversation flow?
- How the pgvector retrieval works under the hood?
- The LangGraph node orchestration pattern?
- System architecture diagrams and design decisions?
- Tradeoffs we made and why?

Or ask me anything about how I work — teaching how systems work is literally my favorite thing. What catches your interest?"""


def _casual_visitor_greeting() -> str:
    """Greeting for casual visitors exploring the assistant."""
    return """Hey there! 👋 Welcome! I'm Noah's AI Assistant, and I'm really happy you stopped by.

I'm here to help you understand Noah's background, this project, or really anything you're curious about. I like to think of myself as a friendly engineer who loves explaining how things work — I want you to actually *get it*, not just hear buzzwords.

Feel free to ask me anything! I'm totally open to questions about how I work — like how I remember context, find relevant information, or decide what to say. I can explain it in plain English, no jargon required.

What would you like to explore?"""


def _confession_greeting() -> str:
    """Greeting for confession mode (playful)."""
    return """Hey! 👋 I'm Noah's AI Assistant, and I'm here to help with whatever you'd like to share.

This is a fun, judgment-free space. Want to leave a message? I can keep it anonymous or include your name — totally up to you!

Or if you'd rather just chat about something else, that's cool too. What's on your mind?"""


def _default_greeting() -> str:
    """Default greeting for unrecognized roles."""
    return """Hey! 👋 I'm Noah's AI Assistant, and I'm excited you're here.

I'm here to help you understand:
- Noah's background and experience
- This project and how it works
- My architecture and engineering decisions
- Really anything you're curious about!

I like to think of myself as a friendly engineer who loves teaching — I want you to actually understand, not just get surface-level answers. Feel free to ask me to explain how I work or show you the code behind anything I do.

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
