"""Action planning logic.

This module decides what follow-up actions to take based on:
- The user's role (hiring manager, developer, etc.)
- What they asked about (technical, career, data, etc.)
- How many turns into the conversation we are

Actions planned here get executed later by action_execution.py.

Junior dev note: This is like a "shopping list" builder. We figure out
what we need to do (send resume, show code, offer LinkedIn) and add it
to a list. The actual work happens in a later step.
"""

from typing import Any
from src.flows.conversation_state import ConversationState
from src.flows.query_classification import _is_data_display_request


def plan_actions(state: ConversationState) -> ConversationState:
    """Decide what follow-up actions to take for this query.
    
    This looks at:
    - state.role: Who is the user? (Hiring Manager, Developer, etc.)
    - query_type: What did they ask about? (technical, career, data, etc.)
    - user_turns: How many times have they asked questions?
    - Special flags: Did they explicitly ask for code/resume/analytics?
    
    Then it builds a list of actions to execute, like:
    - "send_resume": Email Noah's resume
    - "render_live_analytics": Show data tables
    - "display_code_snippet": Show implementation code
    - "suggest_technical_role_switch": Recommend switching to tech role
    
    Args:
        state: Current conversation state
        
    Returns:
        Updated state with pending_actions list populated
    """
    # Clear any old actions from previous turns
    state.pending_actions.clear()
    
    # Get context about the query
    query_type = state.fetch("query_type", "general")
    lowered = state.query.lower()
    user_turns = sum(1 for message in state.chat_history if message.get("role") == "user")
    
    # Check for special request flags
    code_display_requested = state.fetch("code_display_requested", False)
    import_explanation_requested = state.fetch("import_explanation_requested", False)
    
    # Helper to add actions to the list
    def add_action(action_type: str, **extras: Any) -> None:
        state.append_pending_action({"type": action_type, **extras})

    # Detect specific user requests
    resume_requested = any(key in lowered for key in ["send resume", "email resume", "resume", "cv"])
    linkedin_requested = any(key in lowered for key in ["linkedin", "link me", "profile"])
    contact_requested = any(key in lowered for key in ["reach out", "contact me", "call me", "follow up"])
    
    # Detect product/how-it-works questions
    product_question = any(term in lowered for term in [
        "how does this work", "how does it work", "how does", "how is this",
        "what is this", "what does this", "explain this",
        "how is this built", "tell me about this", "what's this"
    ]) or ("product" in lowered and any(word in lowered for word in ["how", "what", "explain", "work"]))

    # Handle data display requests (show analytics/metrics)
    if _is_data_display_request(lowered):
        add_action("render_live_analytics")
        state.stash("data_display_requested", True)

    # Handle direct requests for resources
    if resume_requested:
        add_action("send_resume")
        add_action("ask_reach_out")
        add_action("notify_resume_sent")
        state.stash("offer_sent", True)
    
    if linkedin_requested:
        add_action("send_linkedin")
        if not state.fetch("offer_sent"):
            add_action("ask_reach_out")
            state.stash("offer_sent", True)
    
    if contact_requested:
        add_action("notify_contact_request")
        state.stash("contact_requested", True)

    # Handle code and import explanation requests
    if code_display_requested and state.role in ["Hiring Manager (technical)", "Software Developer"]:
        add_action("display_code_snippet")
    
    if import_explanation_requested:
        add_action("explain_imports")

    # Add QA strategy for product questions (all technical roles)
    if product_question and state.role in ["Hiring Manager (technical)", "Software Developer"]:
        add_action("include_qa_strategy")

    # Role-specific action planning
    if state.role == "Hiring Manager (nontechnical)":
        # Suggest switching to technical role if they ask technical questions
        if query_type == "technical" or code_display_requested or import_explanation_requested or product_question:
            add_action("suggest_technical_role_switch")
        
        # Offer resume after a few turns
        if not resume_requested and not linkedin_requested and user_turns >= 2:
            add_action("offer_resume_prompt")
    
    elif state.role == "Hiring Manager (technical)":
        # For technical/data questions, show full enterprise context
        if query_type in {"technical", "data"}:
            add_action("include_purpose_overview")
            add_action("include_architecture_overview")
            add_action("summarize_data_strategy")
            add_action("provide_data_tables")
            add_action("explain_enterprise_usage")
            add_action("explain_stack_currency")
            add_action("highlight_enterprise_adaptability")
            
            # Auto-display code for technical queries if not already requested
            if not code_display_requested:
                add_action("include_code_snippets")
        
        # Offer resume after a few turns
        if not resume_requested and not linkedin_requested and user_turns >= 2:
            add_action("offer_resume_prompt")
    
    elif state.role == "Software Developer":
        # Developers get code-heavy responses
        if query_type in {"technical", "data"}:
            add_action("include_purpose_overview")
            add_action("include_code_snippets")
            add_action("summarize_data_strategy")
            add_action("provide_data_tables")
            add_action("explain_stack_currency")
            add_action("highlight_enterprise_adaptability")
    
    elif state.role == "Just looking around":
        # Casual visitors get fun content
        if query_type == "mma":
            add_action("share_mma_link")
        else:
            add_action("share_fun_facts")
    
    elif state.role == "Looking to confess crush":
        # Special confession flow
        add_action("collect_confession")

    return state
