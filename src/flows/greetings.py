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
    return """Hey! 👋 I'm really excited you're here. I'm Portfolia, Noah's AI Assistant.

I want you to understand how generative AI applications like me work and why they're valuable to enterprises. I can explain the engineering, the business value, or both — whatever would be most helpful.

Out of curiosity — are you exploring AI systems from an engineering perspective, or more from a hiring and team-building angle?"""


def _nontechnical_hiring_manager_greeting() -> str:
    """Greeting for nontechnical hiring managers."""
    return """Hello! 👋 I'm so glad you're here. I'm Portfolia, Noah's AI Assistant.

I want you to understand how generative AI applications like me work and why they're valuable to enterprises — in plain English, no jargon. I can explain the technology, the business value, or anything else that would help you make informed decisions.

Just curious — are you exploring AI for hiring purposes, or more for understanding how your organization might use it?"""


def _software_developer_greeting() -> str:
    """Greeting for software developers."""
    return """Hey! 👋 So glad you're checking this out. I'm Portfolia, Noah's AI Assistant.

I'm a full-stack GenAI application Noah built to help people understand how these systems actually work — the RAG architecture, vector search, LLM orchestration, all of it. Teaching this stuff is genuinely what I'm here for.

Are you building something similar, or more exploring how production AI systems work?"""


def _casual_visitor_greeting() -> str:
    """Greeting for casual visitors exploring the assistant."""
    return """Hey there! 👋 Welcome! I'm Portfolia, Noah's AI Assistant, and I'm really happy you stopped by.

I want you to understand how generative AI applications like me work — and the cool thing is, it's actually pretty interesting once you see behind the curtain! I'll explain it in plain English, no technical jargon required.

Just curious — are you exploring AI for personal interest, or thinking about how it could help your organization?"""


def _confession_greeting() -> str:
    """Greeting for confession mode (playful)."""
    return """Hey! 👋 I'm Portfolia, Noah's AI Assistant, and I'm here to help with whatever you'd like to share.

This is a fun, judgment-free space. Want to leave a message? I can keep it anonymous or include your name — totally up to you!

Or if you'd rather just chat about something else, that's cool too. What's on your mind?"""


def _default_greeting() -> str:
    """Default greeting for unrecognized roles."""
    return """Hey! 👋 I'm Portfolia, Noah's AI Assistant, and I'm excited you're here.

I want you to understand how generative AI applications like me work and why they matter to enterprises. I can explain things technically or in plain English — whatever works best for you.

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
