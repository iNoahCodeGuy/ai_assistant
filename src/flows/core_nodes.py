"""Core conversation nodes - the main pipeline.

This module contains the essential conversation flow nodes:
1. retrieve_chunks - Get relevant knowledge from the database
2. generate_answer - Create LLM response with retrieved context
3. apply_role_context - Add role-specific content (code, data, links)
4. log_and_notify - Save analytics and trigger notifications

Junior dev note: These are the "middle" of the pipeline. They sit between
query classification (query_classification.py) and action execution (action_execution.py).

For the full flow, see: docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md
"""

import logging
import os
from typing import Dict, Any

from src.state.conversation_state import ConversationState
from src.core.rag_engine import RagEngine
from src.analytics.supabase_analytics import supabase_analytics, UserInteractionData
from src.flows import content_blocks
from src.flows.data_reporting import render_full_data_report
from src.flows.code_validation import is_valid_code_snippet, sanitize_generated_answer

# Setup logger
logger = logging.getLogger(__name__)

# Import retriever with graceful fallback (optional dependency)
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

    # Provide stub functions so code doesn't break
    def search_import_explanations(*args, **kwargs):
        return []
    def detect_import_in_query(*args, **kwargs):
        return None
    def get_import_explanation(*args, **kwargs):
        return None


# Environment config
RESUME_DOWNLOAD_URL = os.getenv("RESUME_DOWNLOAD_URL", "https://example.com/noah-resume.pdf")
LINKEDIN_URL = os.getenv("LINKEDIN_URL", "https://linkedin.com/in/noahdelacalzada")


def retrieve_chunks(state: ConversationState, rag_engine: RagEngine, top_k: int = 4) -> Dict[str, Any]:
    """Retrieve relevant KB chunks using RAG engine (pgvector).

    Observability: Logs retrieval performance (latency, chunk count, avg similarity)
    Performance: ~300ms typical (embedding + vector search)

    Design Principles:
    - Reliability (#4): Graceful handling if retrieval fails (returns empty chunks)
    - Observability: Logs retrieval metadata for LangSmith tracing
    """
    query = state["query"]

    try:
        chunks = rag_engine.retrieve(query, top_k=top_k)
        state["retrieved_chunks"] = chunks.get("chunks", [])
        state["analytics_metadata"]["retrieval_count"] = len(state["retrieved_chunks"])

        # Observability: Track average similarity score for quality monitoring
        if state["retrieved_chunks"]:
            similarities = [c.get("similarity", 0) for c in state["retrieved_chunks"]]
            avg_similarity = sum(similarities) / len(similarities)
            state["analytics_metadata"]["avg_similarity"] = round(avg_similarity, 3)

            logger.info(f"Retrieved {len(state['retrieved_chunks'])} chunks, avg_similarity={avg_similarity:.3f}")
    except Exception as e:
        # Enhanced error context for debugging
        logger.error(f"Retrieval failed for query '{query[:50]}...': {e}", exc_info=True)
        state["retrieved_chunks"] = []
        state["analytics_metadata"]["retrieval_error"] = str(e)

    return state


def generate_answer(state: ConversationState, rag_engine: RagEngine) -> Dict[str, Any]:
    """Generate an assistant response using retrieved context.

    This is where the LLM creates the actual answer to the user's question.
    It uses the chunks we retrieved in the previous step as context.

    Special cases:
    - For data display requests, we skip LLM generation and fetch live analytics
    - For vague queries with insufficient context, we provide a helpful fallback

    Design Principles:
    - **SRP**: Only generates answer, doesn't retrieve or log
    - **Defensibility**: Fail-fast on missing query, fail-safe on LLM errors
    - **Maintainability**: Separates fallback logic from generation logic
    - **Simplicity (KISS)**: Clear flow - validate → check special cases → generate

    Args:
        state: Current conversation state with query + retrieved chunks
        rag_engine: RAG engine with response generator

    Returns:
        Partial state update dict with 'answer' and optional 'fallback_used' flag

    Raises:
        KeyError: If required 'query' field missing from state
    """
    # Fail-fast: Validate required fields (Defensibility)
    try:
        query = state["query"]
    except KeyError as e:
        logger.error("generate_answer called without query in state")
        raise KeyError("State must contain 'query' field for generation") from e

    # Access optional fields safely (Defensibility)
    retrieved_chunks = state.get("retrieved_chunks", [])
    role = state.get("role", "Just looking around")
    chat_history = state.get("chat_history", [])

    # Initialize update dict (Loose Coupling)
    update: Dict[str, Any] = {}

    # PRIORITY 1: Handle ambiguous queries with Ask Mode clarifying questions
    if state.get("ambiguous_query", False):
        options = state.get("ambiguity_options", [])
        context = state.get("ambiguity_context", "")

        # Format options as a natural question with Portfolia's excitement
        options_text = ", ".join(f"**{opt}**" for opt in options[:-1])
        options_text += f", or **{options[-1]}**" if len(options) > 1 else ""

        clarifying_answer = f"""Oh I love this question! I'd be genuinely excited to talk about Noah's engineering work, but "{query}" is pretty broad and I want to make sure I give you what's most useful.

Are you more interested in: {options_text}?

To make this concrete, let me use **myself** as an example—I'm a complete full-stack AI application Noah built:
- **Frontend**: Streamlit (local) + Next.js (production) with chat UI and session management
- **Backend**: Python API routes + LangGraph orchestration for conversation flow
- **Data Pipelines**: CSV processing → chunking → OpenAI embeddings → pgvector storage
- **Architecture**: RAG system (pgvector semantic search + GPT-4 generation), modular design
- **QA/Testing**: pytest framework with mocking strategies (91/93 tests passing = 98%)
- **Deployment**: Vercel serverless with CI/CD pipeline and cost tracking

Each of these areas has fascinating engineering challenges and business value for enterprises. Which aspect catches your interest? Or curious about something specific?"""

        update["answer"] = clarifying_answer
        update["ambiguous_query_clarified"] = True
        logger.info(f"Asked clarifying question for ambiguous query: '{query}'")
        state.update(update)
        return state

    # For data display requests, we'll fetch live analytics later
    # Just set a placeholder for now
    if state.get("data_display_requested", False):
        update["answer"] = "Fetching live analytics data from Supabase..."
        state.update(update)
        return state

    # Check if we have sufficient context
    # If vague query was expanded but we still have no good matches, help the user
    if state.get("vague_query_expanded", False) and len(retrieved_chunks) == 0:
        expanded_query = state.get("expanded_query", "")

        fallback_answer = f"""I'd love to answer your question about "{query}"!

Could you be more specific? For example:
- If you're curious about my engineering skills, try: "What are your software engineering skills?"
- If you want to know about specific technologies, ask: "What's your experience with Python and AI?"
- If you're wondering about projects, try: "What projects have you built?"
- If you want to understand my architecture approach, ask: "How do you design systems?"

I'm here to help you understand Noah's capabilities and how generative AI applications like me work. What would you like to explore?"""

        update["answer"] = fallback_answer
        update["fallback_used"] = True
        logger.info(f"Used fallback for vague query '{query}' with no matches")
        state.update(update)
        return state

    # Check for very low retrieval quality (all scores below threshold)
    retrieval_scores = state.get("retrieval_scores", [])
    if retrieval_scores and all(score < 0.4 for score in retrieval_scores):
        fallback_answer = f"""I'm not finding great matches for "{query}" in my knowledge base, but I'd love to help!

Here are some things I can tell you about:
- **Noah's engineering skills and experience** - "What are your software engineering skills?"
- **Production GenAI systems** - "What do you understand about production GenAI systems?"
- **System architecture** - "How do you approach system architecture?"
- **Specific projects** - "What projects have you built?"
- **Technical stack and tools** - "What technologies do you use?"
- **Career background** - "Tell me about your career journey"

Or ask me to explain how I work - I love teaching about RAG, vector search, and LLM orchestration! What sounds interesting?"""

        update["answer"] = fallback_answer
        update["fallback_used"] = True
        logger.info(f"Used fallback for low-quality retrieval (scores: {retrieval_scores})")
        state.update(update)
        return state

    # Use the LLM to generate a response with retrieved context
    # Add display intelligence based on query classification
    extra_instructions = []

    # When teaching/explaining, provide comprehensive depth
    if state.get("needs_longer_response", False) or state.get("teaching_moment", False):
        extra_instructions.append(
            "This is a teaching moment - provide a comprehensive, well-structured explanation. "
            "Break down concepts clearly, connect technical details to business value, and "
            "help the user truly understand. Use examples where helpful."
        )

    # EXPLICIT code request - user specifically asked
    if state.get("code_display_requested", False) and role in [
        "Software Developer",
        "Hiring Manager (technical)"
    ]:
        extra_instructions.append(
            "The user has requested code. After your explanation, include relevant code snippets "
            "with comments explaining key decisions. Keep code blocks under 40 lines and focus "
            "on the most interesting parts."
        )
    # PROACTIVE code suggestion - code would clarify but wasn't explicitly requested
    elif state.get("code_would_help", False) and role in [
        "Software Developer",
        "Hiring Manager (technical)"
    ]:
        extra_instructions.append(
            "This technical concept would benefit from a code example. After your explanation, "
            "include a relevant code snippet (≤40 lines) with comments to clarify the implementation. "
            "This is proactive - the user didn't explicitly ask but code will help understanding."
        )

    # EXPLICIT data request - user specifically asked
    if state.get("data_display_requested", False):
        extra_instructions.append(
            "The user wants data/analytics. Be brief with narrative - focus on presenting clean "
            "tables with proper formatting. Include source attribution."
        )
    # PROACTIVE data suggestion - metrics would clarify but weren't explicitly requested
    elif state.get("data_would_help", False):
        extra_instructions.append(
            "This question would benefit from actual metrics/data. After your explanation, "
            "include relevant analytics in table format if available. Be concise with tables, "
            "include source attribution. This is proactive - help the user with concrete numbers."
        )

    # Job details gathering (AFTER resume sent) - Task 9
    # Import here to avoid circular dependency
    from src.flows.resume_distribution import should_gather_job_details, get_job_details_prompt

    if should_gather_job_details(state):
        extra_instructions.append(get_job_details_prompt())

    # Build the instruction suffix
    instruction_suffix = " ".join(extra_instructions) if extra_instructions else None

    # Generate response with LLM (Encapsulation - delegates to response generator)
    try:
        answer = rag_engine.response_generator.generate_contextual_response(
            query=query,
            context=retrieved_chunks,
            role=role,
            chat_history=chat_history,
            extra_instructions=instruction_suffix
        )
    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        # Fail-safe: Provide graceful error message (Defensibility)
        answer = (
            "I'm having trouble generating a response right now. "
            "Please try rephrasing your question or ask something else!"
        )

    # Clean up any SQL artifacts that leaked from retrieval (Maintainability)
    update["answer"] = sanitize_generated_answer(answer)

    # Update state in-place (current functional pipeline pattern)
    # When we migrate to LangGraph StateGraph, this will return partial dict only
    state.update(update)
    return state


def apply_role_context(state: ConversationState, rag_engine: RagEngine) -> Dict[str, Any]:
    """Add role-specific content blocks to the answer.

    This is where we enrich the base answer with extra content based on
    the actions we planned earlier. For example:
    - Add code snippets for developers
    - Add architecture diagrams for technical roles
    - Add fun facts for casual visitors
    - Add resume links when requested

    Design Principles:
    - **SRP**: Only enriches answer with content blocks, doesn't generate
    - **Maintainability**: Uses content_blocks module for reusable components
    - **Extensibility**: Easy to add new action types
    - **Simplicity (DRY)**: Centralizes all content block assembly

    Args:
        state: Current conversation state with answer + pending_actions
        rag_engine: RAG engine for code retrieval

    Returns:
        Partial state update dict with enriched 'answer' and optional metadata

    Raises:
        KeyError: If required 'answer' field missing from state
    """
    # Fail-fast: Validate required fields (Defensibility)
    try:
        base_answer = state["answer"]
    except KeyError as e:
        logger.error("apply_role_context called without answer in state")
        raise KeyError("State must contain 'answer' field for enrichment") from e

    # If no answer, skip enrichment (fail-safe)
    if not base_answer:
        return {}  # No update needed

    # Access optional fields safely (Defensibility)
    pending_actions = state.get("pending_actions", [])
    query_type = state.get("query_type", "general")
    role = state.get("role", "Just looking around")
    query = state.get("query", "")

    # Start with the base answer, we'll append blocks to it
    components = [base_answer]
    actions = {action["type"] for action in pending_actions}

    # Enterprise-focused content blocks (for hiring managers + developers)
    if "include_purpose_overview" in actions:
        components.append(
            "\n\n" + content_blocks.format_section("Product Purpose", content_blocks.purpose_block())
        )

    if "include_qa_strategy" in actions:
        components.append(
            "\n\n" + content_blocks.format_section("Quality Assurance", content_blocks.qa_strategy_block())
        )

    # Live analytics rendering (replaces placeholder)
    if "render_live_analytics" in actions:
        try:
            import requests
            from src.config.supabase_config import supabase_settings

            # Determine analytics API URL (production vs local)
            if supabase_settings.is_vercel:
                analytics_url = "https://noahsaiassistant.vercel.app/api/analytics"
            else:
                analytics_url = "http://localhost:3000/api/analytics"

            # Fetch live data
            response = requests.get(analytics_url, timeout=3)
            response.raise_for_status()
            analytics_data = response.json()

            # Render with role-appropriate formatting
            from src.flows.analytics_renderer import render_live_analytics
            analytics_report = render_live_analytics(
                analytics_data,
                state.role,
                focus=None
            )

            # Replace placeholder with actual report
            components = [analytics_report]

        except Exception as e:
            logger.error(f"Failed to fetch live analytics: {e}")
            # Fallback to cached version
            components.append(
                "\n\n⚠️ Live analytics temporarily unavailable. Would you like to see a cached summary?"
            )

    # Legacy data report (for compatibility)
    if "render_data_report" in actions and "render_live_analytics" not in actions:
        report = state.get("data_report")
        if not report:
            report = render_full_data_report()
            # Store for potential reuse in this conversation
        components.append(
            "\n\n" + content_blocks.format_section("Data Insights & Full Dataset", report)
        )

    # Other enterprise content blocks
    if "provide_data_tables" in actions:
        components.append(
            "\n\n" + content_blocks.format_section("Data Collection Overview", content_blocks.data_collection_table())
        )

    if "include_architecture_overview" in actions:
        components.append(
            "\n\n" + content_blocks.format_section("Architecture Snapshot", content_blocks.architecture_snapshot())
        )

    if "summarize_data_strategy" in actions:
        components.append(
            "\n\n" + content_blocks.format_section("Data Management Strategy", content_blocks.data_strategy_block())
        )

    if "explain_enterprise_usage" in actions:
        components.append(
            "\n\n" + content_blocks.format_section("Enterprise Fit", content_blocks.enterprise_fit_explanation())
        )

    if "explain_stack_currency" in actions:
        components.append(
            "\n\n" + content_blocks.format_section("Stack Importance", content_blocks.stack_importance_explanation())
        )

    if "suggest_technical_role_switch" in actions:
        components.append(content_blocks.role_switch_suggestion("Hiring Manager (technical)"))

    if "suggest_developer_role_switch" in actions:
        components.append(content_blocks.role_switch_suggestion("Software Developer"))

    if "highlight_enterprise_adaptability" in actions:
        components.append(
            "\n\n" + content_blocks.format_section("Enterprise Adaptability", content_blocks.enterprise_adaptability_block())
        )

    # Casual content blocks (for "Just looking around" role)
    if "share_fun_facts" in actions:
        components.append(
            "\n\n" + content_blocks.format_section("Fun Facts About Noah", content_blocks.fun_facts_block())
        )

    if "share_mma_link" in actions or query_type == "mma":
        components.append("\n\n" + content_blocks.mma_fight_link())

    # Resource offers (LinkedIn, resume)
    if "send_linkedin" in actions:
        components.append(f"\n\nHere is Noah's LinkedIn profile: {LINKEDIN_URL}")
        # Note: offer_sent tracked elsewhere (action execution)

    if "send_resume" in actions:
        resume_link = state.get("resume_signed_url", RESUME_DOWNLOAD_URL)
        components.append(f"\n\nDownload Noah's resume: {resume_link}")
        # Note: offer_sent tracked elsewhere (action execution)

    # Code snippets (for developers and technical hiring managers)
    if "include_code_snippets" in actions or "display_code_snippet" in actions:
        try:
            results = rag_engine.retrieve_with_code(query, role=role)
            snippets = results.get("code_snippets", []) if results else []
        except Exception as e:
            logger.warning(f"Code retrieval failed: {e}")
            snippets = []

        if snippets:
            snippet = snippets[0]
            code_content = snippet.get("content", "")
            citation = snippet.get("citation", "codebase")

            # Validate it's real code (not metadata)
            if is_valid_code_snippet(code_content):
                formatted_code = content_blocks.format_code_snippet(
                    code=code_content,
                    file_path=citation,
                    language="python",
                    description="Implementation showing the core logic referenced in your question"
                )
                components.append(f"\n\n**Code Implementation**\n{formatted_code}")
                components.append(content_blocks.code_display_guardrails())
            else:
                # Code index is empty or malformed
                components.append(
                    "\n\n"
                    + content_blocks.format_section(
                        "Code Display Unavailable",
                        "The code index is being refreshed right now. In the meantime you can:\n"
                        "- Browse the codebase on GitHub: https://github.com/iNoahCodeGuy/ai_assistant\n"
                        "- Ask for architecture explanations or design walkthroughs\n"
                        "- Request high-level summaries of how components interact"
                    )
                )
        else:
            # No code found for this query
            if "display_code_snippet" in actions:
                components.append(
                    "\n\n"
                    + content_blocks.format_section(
                        "No Matching Code",
                        "I couldn't find code matching that request. You can:\n"
                        "- Browse the full codebase: https://github.com/iNoahCodeGuy/ai_assistant\n"
                        "- Ask for an architectural overview or diagram\n"
                        "- Request insights into specific features or services"
                    )
                )

    # Import/stack explanations (why did you choose X library?)
    if "explain_imports" in actions:
        import_name = detect_import_in_query(query)

        if import_name:
            # Get specific explanation for this import
            explanation_data = get_import_explanation(import_name, role)
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
            # Search for relevant imports
            relevant_imports = search_import_explanations(query, role, top_k=3)
            if relevant_imports:
                components.append("\n\n**Stack Justifications**\n")
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

    # Interactive prompts (ask if they want resume, outreach, etc.)
    if "offer_resume_prompt" in actions and not state.get("offer_sent"):
        components.append("\n\nWould you like me to email you my resume or share my LinkedIn profile?")

    if "ask_reach_out" in actions:
        components.append("\n\nWould you like Noah to reach out?")

    if "collect_confession" in actions:
        components.append(
            "\n\n💌 Your message is safe. You can submit anonymously or include your name and contact info, and I'll pass it along with a private SMS to Noah."
        )

    # Technical follow-up prompt (for technical roles)
    if (
        query_type in {"technical", "data"}
        and role in {"Hiring Manager (technical)", "Software Developer"}
    ):
        components.append(
            "\n\nWould you like me to go into further detail about the logic behind the architecture, display data collected, or go deeper on how a project like this could be adapted into enterprise use?"
        )

    # Combine all components into final enriched answer
    enriched_answer = "".join(components)

    # Update state in-place (current functional pipeline pattern)
    # When we migrate to LangGraph StateGraph, this will return partial dict only
    state["answer"] = enriched_answer
    return state


def log_and_notify(
    state: ConversationState,
    session_id: str,
    latency_ms: int,
    success: bool = True
) -> Dict[str, Any]:
    """Save analytics to Supabase and trigger notifications.

    This is the last step in the pipeline. It records the conversation
    to the database for evaluation and potential follow-up.

    Design Principles:
    - **SRP**: Only handles analytics logging, doesn't modify answer
    - **Defensibility**: Gracefully handles logging failures
    - **Loose Coupling**: Returns partial update with metadata only

    Args:
        state: Current conversation state with final answer
        session_id: Unique session identifier
        latency_ms: How long the conversation took
        success: Whether the conversation completed successfully

    Returns:
        Partial state update dict with analytics metadata
    """
    # Access required fields with fail-safe defaults
    role = state.get("role", "Just looking around")
    query = state.get("query", "")
    answer = state.get("answer", "")
    query_type = state.get("query_type", "general")

    # Initialize update dict
    update: Dict[str, Any] = {}

    try:
        interaction = UserInteractionData(
            session_id=session_id,
            role_mode=role,
            query=query,
            answer=answer,
            query_type=query_type,
            latency_ms=latency_ms,
            success=success
        )
        message_id = supabase_analytics.log_interaction(interaction)

        # Store analytics metadata in state (inside analytics_metadata dict)
        if "analytics_metadata" not in state:
            state["analytics_metadata"] = {}
        state["analytics_metadata"]["message_id"] = message_id
        state["analytics_metadata"]["logged_at"] = True
    except Exception as exc:
        logger.error("Failed logging analytics: %s", exc)
        if "analytics_metadata" not in state:
            state["analytics_metadata"] = {}
        state["analytics_metadata"]["logged_at"] = False

    # Note: update dict no longer needed since we write directly to state
    # When we migrate to LangGraph StateGraph, this will return partial dict only
    return state
