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

I can walk you through:
- How my RAG pipeline works (pgvector + LangGraph orchestration)
- The data contracts and analytics strategy
- How this could scale in an enterprise context
- Noah's technical background and experience
- Or anything else you're curious about!

I'm also happy to explain how I was built, my architecture, or dive into specific technical decisions. What sounds interesting?"""


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

Want to see:
- Code snippets from the RAG engine or conversation flow?
- How the pgvector retrieval works under the hood?
- The LangGraph node orchestration pattern?
- System architecture diagrams?
- Noah's technical projects and contributions?

Or ask me anything about how I work — I love talking about the engineering! What catches your interest?"""


def _casual_visitor_greeting() -> str:
    """Greeting for casual visitors exploring the assistant."""
    return """Hey there! 👋 Welcome! I'm Noah's AI Assistant, and I'm really happy you stopped by.

I'm here to tell you about Noah's background, this project, or really anything you're curious about. I'm also totally open to questions about how I work — like how I remember context, find relevant information, or decide what to say.

Feel free to ask me anything! What would you like to explore?"""


def _confession_greeting() -> str:
    """Greeting for confession mode (playful)."""
    return """Hey! 👋 I'm Noah's AI Assistant, and I'm here to help with whatever you'd like to share.

This is a fun, judgment-free space. Want to leave a message? I can keep it anonymous or include your name — totally up to you!

Or if you'd rather just chat about something else, that's cool too. What's on your mind?"""


def _default_greeting() -> str:
    """Default greeting for unrecognized roles."""
    return """Hey! 👋 I'm Noah's AI Assistant, and I'm excited you're here.

I can tell you about:
- Noah's background and experience
- This project and how it works
- My architecture and engineering decisions
- Or answer any questions you have!

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
