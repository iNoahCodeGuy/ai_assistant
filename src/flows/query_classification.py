"""Query classification utilities.

This module detects what kind of question the user is asking so we can
route it appropriately and plan the right follow-up actions.

Types we detect:
- Technical queries (architecture, code, stack questions)
- Career queries (resume, experience, achievements)
- Data display requests (show analytics, metrics)
- MMA queries (Noah's fight history)
- Fun queries (hobbies, fun facts)
"""

import re
from src.flows.conversation_state import ConversationState


DATA_DISPLAY_KEYWORDS = [
    "display data",
    "show data",
    "show me the data",
    "display analytics",
    "data collected",
    "collected data",
    "display collected data",
    "share the data",
    "show analytics",
    "can you display",
]


def _is_data_display_request(lowered_query: str) -> bool:
    """Check if query requests data/analytics display."""
    return any(keyword in lowered_query for keyword in DATA_DISPLAY_KEYWORDS)


def classify_query(state: ConversationState) -> ConversationState:
    """Classify the incoming query and stash the result on state.
    
    This is the first node in the conversation pipeline. It looks at the
    user's question and figures out what category it falls into.
    
    Detects:
    - Code display requests (show/display code, how do you, implementation details)
    - Import/stack questions (why use X, what imports, explain dependencies)
    - Technical queries (architecture, retrieval, pipeline)
    - Career queries (resume, experience, achievements)
    - MMA queries (fight references)
    - Data display requests (show analytics, display data)
    - Fun queries (fun facts, hobbies)
    
    Args:
        state: Current conversation state with the user's query
        
    Returns:
        Updated state with query_type and relevant flags stashed
    """
    lowered = state.query.lower()
    
    # Code display triggers (explicit requests to see code)
    code_display_keywords = [
        "show code", "display code", "show me code", "show the code",
        "show implementation", "display implementation",
        "how do you", "how does it", "how is it",
        "show me the", "show retrieval", "show api",
        "code snippet", "code example", "source code"
    ]
    if any(keyword in lowered for keyword in code_display_keywords):
        state.stash("code_display_requested", True)
        state.stash("query_type", "technical")
    
    # Import/stack explanation triggers (why did you choose X?)
    import_keywords = [
        "why use", "why choose", "why did you use", "why did you choose",
        "what imports", "explain imports", "your imports", "dependencies",
        "why supabase", "why openai", "why langchain", "why vercel",
        "why pgvector", "why twilio", "why resend",
        "justify", "trade-off", "alternative", "vs", "instead of",
        "enterprise", "production", "scale", "library", "libraries"
    ]
    
    # Specific library mentions
    library_names = [
        "supabase", "openai", "pgvector", "langchain", "langgraph", 
        "vercel", "resend", "twilio", "langsmith", "streamlit"
    ]
    
    if any(keyword in lowered for keyword in import_keywords):
        state.stash("import_explanation_requested", True)
        state.stash("query_type", "technical")
    elif any(lib in lowered for lib in library_names) and any(word in lowered for word in ["why", "what", "how", "explain"]):
        state.stash("import_explanation_requested", True)
        state.stash("query_type", "technical")
    
    # Query type classification
    if any(re.search(r"\\b" + k + r"\\b", lowered) for k in ["mma", "fight", "ufc", "bout", "cage"]):
        state.stash("query_type", "mma")
    elif any(term in lowered for term in ["fun fact", "hobby", "interesting fact", "hot dog"]):
        state.stash("query_type", "fun")
    elif _is_data_display_request(lowered):
        state.stash("data_display_requested", True)
        state.stash("query_type", "data")
    # Detect "how does [product/system/chatbot] work" queries as technical
    elif any(term in lowered for term in ["code", "technical", "stack", "architecture", "implementation", "retrieval"]) \
         or (("how does" in lowered or "how did" in lowered or "explain how" in lowered) 
             and any(word in lowered for word in ["product", "system", "chatbot", "assistant", "rag", "pipeline", "work", "built"])):
        state.stash("query_type", "technical")
    elif any(term in lowered for term in ["career", "resume", "cv", "experience", "achievement", "work"]):
        state.stash("query_type", "career")
    else:
        state.stash("query_type", "general")
    
    return state
