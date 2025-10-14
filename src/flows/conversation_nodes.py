"""Composable conversation nodes for the LangGraph migration path.

This module implements the core conversation flow as a series of pure functions
(nodes) that transform ConversationState. Each node has a single responsibility:

1. classify_query - Detect query intent (technical, career, MMA, data, etc.)
2. retrieve_chunks - Fetch relevant knowledge base content via RAG
3. generate_answer - Create LLM response using retrieved context
4. plan_actions - Determine follow-up actions (resume, data display, notifications)
5. apply_role_context - Enrich answer with role-specific content blocks
6. execute_actions - Perform side effects (emails, SMS, storage)
7. log_and_notify - Persist analytics and trigger downstream systems

Design principles:
- Immutable state updates via ConversationState methods
- Defensive error handling with graceful degradation
- Modular content generation (see content_blocks.py)
- Separated side effects (see action_execution.py)
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any

from src.flows.conversation_state import ConversationState
from src.core.rag_engine import RagEngine
from src.analytics.supabase_analytics import supabase_analytics, UserInteractionData
from src.flows import content_blocks
from src.flows.data_reporting import render_full_data_report
from src.flows.action_execution import execute_actions

# Setup logger
logger = logging.getLogger(__name__)

# Import retriever with graceful fallback
try:
    from src.retrieval.import_retriever import (
        search_import_explanations,
        detect_import_in_query,
        get_import_explanation
    )
    IMPORT_RETRIEVER_AVAILABLE = True
except Exception as e:
    logger.warning(f"Import retriever not available: {e}")
    IMPORT_RETRIEVER_AVAILABLE = False
    # Provide stub functions
    def search_import_explanations(*args, **kwargs):
        return []
    def detect_import_in_query(*args, **kwargs):
        return None
    def get_import_explanation(*args, **kwargs):
        return None

logger = logging.getLogger(__name__)

RESUME_DOWNLOAD_URL = os.getenv("RESUME_DOWNLOAD_URL", "https://example.com/noah-resume.pdf")
LINKEDIN_URL = os.getenv("LINKEDIN_URL", "https://linkedin.com/in/noahdelacalzada")

DATA_DISPLAY_KEYWORDS = [
    "display data",
    "show data",
    "show me the data",
    "display analytics",
    "data collected",
    "share the data",
    "show analytics",
]


def _is_data_display_request(lowered_query: str) -> bool:
    """Check if query requests data/analytics display."""
    return any(keyword in lowered_query for keyword in DATA_DISPLAY_KEYWORDS)


def classify_query(state: ConversationState) -> ConversationState:
    """Classify the incoming query and stash the result on state.
    
    Detects:
    - Code display requests (show/display code, how do you, implementation details)
    - Import/stack questions (why use X, what imports, explain dependencies)
    - Technical queries (architecture, retrieval, pipeline)
    - Career queries (resume, experience, achievements)
    - MMA queries (fight references)
    - Data display requests (show analytics, display data)
    - Fun queries (fun facts, hobbies)
    """
    lowered = state.query.lower()
    
    # Code display triggers (explicit requests)
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
    
    # Import/stack explanation triggers
    import_keywords = [
        "why use", "why choose", "why did you use", "why did you choose",
        "what imports", "explain imports", "your imports", "dependencies",
        "why supabase", "why openai", "why langchain", "why vercel",
        "why pgvector", "why twilio", "why resend",
        "justify", "trade-off", "alternative", "vs", "instead of",
        "enterprise", "production", "scale", "library", "libraries"
    ]
    # Also check for specific library mentions in query
    library_names = ["supabase", "openai", "pgvector", "langchain", "langgraph", 
                     "vercel", "resend", "twilio", "langsmith", "streamlit"]
    
    if any(keyword in lowered for keyword in import_keywords):
        state.stash("import_explanation_requested", True)
        state.stash("query_type", "technical")
    # If query mentions a library name directly, likely asking about it
    elif any(lib in lowered for lib in library_names) and any(word in lowered for word in ["why", "what", "how", "explain"]):
        state.stash("import_explanation_requested", True)
        state.stash("query_type", "technical")
    
    # Query type classification
    if any(re.search(r"\\b" + k + r"\\b", lowered) for k in ["mma", "fight", "ufc", "bout", "cage"]):
        state.stash("query_type", "mma")
    elif any(term in lowered for term in ["fun fact", "hobby", "interesting fact", "hot dog"]):
        state.stash("query_type", "fun")
    elif _is_data_display_request(lowered):
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


def retrieve_chunks(state: ConversationState, rag_engine: RagEngine, top_k: int = 4) -> ConversationState:
    """Retrieve knowledge base chunks and store them on state."""
    results = rag_engine.retrieve(state.query, top_k=top_k)
    state.add_retrieved_chunks(results.get("chunks", []))
    state.stash("retrieval_matches", results.get("matches", []))
    state.stash("retrieval_scores", results.get("scores", []))
    return state


def generate_answer(state: ConversationState, rag_engine: RagEngine) -> ConversationState:
    """Generate an assistant response using retrieved context.
    
    Uses contextual response generation which includes:
    - Role-aware prompting
    - Third-person language enforcement
    - Technical follow-up questions (for technical roles)
    """
    # Get retrieved chunks for context
    retrieved_chunks = state.retrieved_chunks or []
    
    # Use contextual response generator (includes follow-ups)
    answer = rag_engine.response_generator.generate_contextual_response(
        query=state.query,
        context=retrieved_chunks,
        role=state.role
    )
    
    state.set_answer(answer)
    return state


def plan_actions(state: ConversationState) -> ConversationState:
    """Derive follow-up actions (resume offers, tables, notifications, code display)."""
    state.pending_actions.clear()
    query_type = state.fetch("query_type", "general")
    lowered = state.query.lower()
    user_turns = sum(1 for message in state.chat_history if message.get("role") == "user")
    
    # Check for code/import request flags
    code_display_requested = state.fetch("code_display_requested", False)
    import_explanation_requested = state.fetch("import_explanation_requested", False)

    def add_action(action_type: str, **extras: Any) -> None:
        state.append_pending_action({"type": action_type, **extras})

    resume_requested = any(key in lowered for key in ["send resume", "email resume", "resume", "cv"])
    linkedin_requested = any(key in lowered for key in ["linkedin", "link me", "profile"])
    contact_requested = any(key in lowered for key in ["reach out", "contact me", "call me", "follow up"])

    if _is_data_display_request(lowered):
        add_action("render_data_report")
        state.stash("data_display_requested", True)

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

    # Code display and import explanations for technical roles
    if code_display_requested and state.role in ["Hiring Manager (technical)", "Software Developer"]:
        add_action("display_code_snippet")
    
    if import_explanation_requested:
        add_action("explain_imports")

    if state.role == "Hiring Manager (nontechnical)":
        if not resume_requested and not linkedin_requested and user_turns >= 2:
            add_action("offer_resume_prompt")
    elif state.role == "Hiring Manager (technical)":
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
        if not resume_requested and not linkedin_requested and user_turns >= 2:
            add_action("offer_resume_prompt")
    elif state.role == "Software Developer":
        if query_type in {"technical", "data"}:
            add_action("include_purpose_overview")
            add_action("include_code_snippets")
            add_action("summarize_data_strategy")
            add_action("provide_data_tables")
            add_action("explain_stack_currency")
            add_action("highlight_enterprise_adaptability")
    elif state.role == "Just looking around":
        if query_type == "mma":
            add_action("share_mma_link")
        else:
            add_action("share_fun_facts")
    elif state.role == "Looking to confess crush":
        add_action("collect_confession")

    return state


def apply_role_context(state: ConversationState, rag_engine: RagEngine) -> ConversationState:
    """Tailor the generated answer with role-specific enrichments.
    
    This node appends structured content blocks based on planned actions:
    - Product purpose and enterprise signal
    - Full data analytics report
    - Architecture and stack explanations
    - Fun facts and MMA links
    - Resume and LinkedIn offers
    - Code snippets for developers
    
    Args:
        state: Current conversation state
        rag_engine: RAG engine for code retrieval
        
    Returns:
        Updated state with enriched answer
    """
    if not state.answer:
        return state

    components = [state.answer]
    actions = {action["type"] for action in state.pending_actions}
    query_type = state.fetch("query_type", "general")

    # Enterprise-focused content blocks
    if "include_purpose_overview" in actions:
        components.append("\n\n### 🎯 Product Purpose\n" + content_blocks.purpose_block())

    if "render_data_report" in actions:
        report = state.fetch("data_report")
        if not report:
            report = render_full_data_report()
            state.stash("data_report", report)
        components.append("\n\n### 📈 Data Insights & Full Dataset\n" + report)

    if "provide_data_tables" in actions:
        components.append("\n\n### 📊 Data Collection Overview\n" + content_blocks.data_collection_table())

    if "include_architecture_overview" in actions:
        components.append("\n\n### 🏗️ Architecture Snapshot\n" + content_blocks.architecture_snapshot())

    if "summarize_data_strategy" in actions:
        components.append("\n\n### 🗂️ Data Management Strategy\n" + content_blocks.data_strategy_block())

    if "explain_enterprise_usage" in actions:
        components.append("\n\n### 🏢 Enterprise Fit\n" + content_blocks.enterprise_fit_explanation())

    if "explain_stack_currency" in actions:
        components.append("\n\n### 🧱 Stack Importance\n" + content_blocks.stack_importance_explanation())

    if "highlight_enterprise_adaptability" in actions:
        components.append("\n\n### 🚀 Enterprise Adaptability\n" + content_blocks.enterprise_adaptability_block())

    # Casual content blocks
    if "share_fun_facts" in actions:
        components.append("\n\n### 🎉 Fun Facts\n" + content_blocks.fun_facts_block())

    if "share_mma_link" in actions or query_type == "mma":
        components.append("\n\n" + content_blocks.mma_fight_link())

    # Resource offers
    if "send_linkedin" in actions:
        components.append(f"\n\nHere is Noah's LinkedIn profile: {LINKEDIN_URL}")
        state.stash("offer_sent", True)

    if "send_resume" in actions:
        resume_link = state.fetch("resume_signed_url", RESUME_DOWNLOAD_URL)
        components.append(f"\n\nDownload Noah's resume: {resume_link}")
        state.stash("offer_sent", True)

    # Code snippets for developers
    if "include_code_snippets" in actions or "display_code_snippet" in actions:
        try:
            results = rag_engine.retrieve_with_code(state.query, role=state.role)
            snippets = results.get("code_snippets", []) if results else []
        except Exception:  # pragma: no cover - defensive guard
            snippets = []
        if snippets:
            snippet = snippets[0]
            code_content = snippet.get("content", "")
            citation = snippet.get("citation", "codebase")
            
            # Use formatted code display with enterprise prompt
            formatted_code = content_blocks.format_code_snippet(
                code=code_content,
                file_path=citation,
                language="python",
                description="Implementation showing the core logic referenced in your question"
            )
            components.append(f"\n\n### 💻 Code Implementation\n{formatted_code}")
            components.append(content_blocks.code_display_guardrails())
    
    # Import explanations for stack questions
    if "explain_imports" in actions:
        # Detect which import they're asking about
        import_name = detect_import_in_query(state.query)
        
        if import_name:
            # Get tier-appropriate explanation
            explanation_data = get_import_explanation(import_name, state.role)
            if explanation_data:
                formatted_explanation = content_blocks.format_import_explanation(
                    import_name=explanation_data["import"],
                    tier=explanation_data["tier"],
                    explanation=explanation_data["explanation"],
                    enterprise_concern=explanation_data.get("enterprise_concern", ""),
                    enterprise_alternative=explanation_data.get("enterprise_alternative", ""),
                    when_to_switch=explanation_data.get("when_to_switch", "")
                )
                components.append(f"\n\n{formatted_explanation}")
        else:
            # Search for relevant imports based on query
            relevant_imports = search_import_explanations(state.query, state.role, top_k=3)
            if relevant_imports:
                components.append("\n\n### 📦 Stack Justifications\n")
                for imp_data in relevant_imports:
                    formatted = content_blocks.format_import_explanation(
                        import_name=imp_data["import"],
                        tier=imp_data["tier"],
                        explanation=imp_data["explanation"],
                        enterprise_concern=imp_data.get("enterprise_concern", ""),
                        enterprise_alternative=imp_data.get("enterprise_alternative", ""),
                        when_to_switch=imp_data.get("when_to_switch", "")
                    )
                    components.append(f"\n{formatted}\n")


    # Interactive prompts
    if "offer_resume_prompt" in actions and not state.fetch("offer_sent"):
        components.append("\n\nWould you like me to email you my resume or share my LinkedIn profile?")

    if "ask_reach_out" in actions:
        components.append("\n\nWould you like Noah to reach out?")

    if "collect_confession" in actions:
        components.append(
            "\n\n💌 Your message is safe. You can submit anonymously or include your name and contact info, and I'll pass it along with a private SMS to Noah."
        )

    # Technical follow-up prompt
    if (
        query_type in {"technical", "data"}
        and state.role in {"Hiring Manager (technical)", "Software Developer"}
    ):
        components.append(
            "\n\nWould you like me to go into further detail about the logic behind the architecture, display data collected, or go deeper on how a project like this could be adapted into enterprise use?"
        )

    state.set_answer("".join(components))
    return state


# execute_actions is imported from action_execution module
# (see imports at top of file)


def log_and_notify(
    state: ConversationState,
    session_id: str,
    latency_ms: int,
    success: bool = True
) -> ConversationState:
    """Persist analytics and trigger downstream notifications."""
    try:
        interaction = UserInteractionData(
            session_id=session_id,
            role_mode=state.role,
            query=state.query,
            answer=state.answer or "",
            query_type=state.fetch("query_type", "general"),
            latency_ms=latency_ms,
            success=success
        )
        message_id = supabase_analytics.log_interaction(interaction)
        state.update_analytics("message_id", message_id)
    except Exception as exc:
        logger.error("Failed logging analytics: %s", exc)

    # Additional notification hooks will be wired as nodes mature.
    return state
