"""Core conversation nodes - retrieval, generation, and analytics layers.

This module houses the retrieval + generation stack for the LangGraph pipeline:
1. retrieve_chunks → Supabase pgvector search
2. re_rank_and_dedup → Lightweight diversification guard
3. validate_grounding / handle_grounding_gap → Early hallucination gate
4. generate_draft → LLM response before formatting
5. hallucination_check → Attach lightweight citations
6. format_answer → Role-aware formatting (replaces apply_role_context)
7. log_and_notify → Persist analytics and retrieval traces
8. suggest_followups → Curiosity prompts
9. update_memory → Store soft session signals

Junior dev note: These are the "middle" of the pipeline. They sit between
query classification (query_classification.py) and action execution (action_execution.py).

For the full flow, see: docs/context/SYSTEM_ARCHITECTURE_SUMMARY.md
"""

import logging
import os
import re
from typing import Dict, Any, List

from src.state.conversation_state import ConversationState
from src.core.rag_engine import RagEngine
from src.analytics.supabase_analytics import (
    supabase_analytics,
    UserInteractionData,
    RetrievalLogData,
)
from src.flows import content_blocks
from src.flows.code_validation import is_valid_code_snippet, sanitize_generated_answer
from src.observability.langsmith_tracer import create_custom_span

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
    query = state.get("composed_query") or state["query"]
    metadata = state.setdefault("analytics_metadata", {})

    with create_custom_span("retrieve_chunks", {"query": query[:120], "top_k": top_k}):
        try:
            chunks = rag_engine.retrieve(query, top_k=top_k) or {}
            raw_chunks = chunks.get("chunks", [])
            normalized: List[Dict[str, Any]] = []

            for item in raw_chunks:
                if isinstance(item, dict):
                    normalized.append(item)
                else:
                    normalized.append({"content": str(item)})

            state["retrieved_chunks"] = normalized

            raw_scores = chunks.get("scores")
            if isinstance(raw_scores, list) and len(raw_scores) == len(normalized):
                scores = [score if isinstance(score, (int, float)) else 0.0 for score in raw_scores]
            else:
                scores = []
                for chunk in normalized:
                    similarity = chunk.get("similarity", 0.0) if isinstance(chunk, dict) else 0.0
                    scores.append(similarity if isinstance(similarity, (int, float)) else 0.0)

            state["retrieval_scores"] = scores
            metadata["retrieval_count"] = len(normalized)

            if scores:
                avg_similarity = sum(scores) / len(scores)
                metadata["avg_similarity"] = round(avg_similarity, 3)
                logger.info(
                    "Retrieved %s chunks, avg_similarity=%.3f",
                    len(state["retrieved_chunks"]),
                    avg_similarity,
                )
        except Exception as e:
            logger.error(
                "Retrieval failed for query '%s...': %s",
                query[:50],
                e,
                exc_info=True,
            )
            state["retrieved_chunks"] = []
            state["retrieval_scores"] = []
            metadata["retrieval_error"] = str(e)

    return state


def re_rank_and_dedup(state: ConversationState) -> ConversationState:
    """Apply lightweight MMR-style diversification to retrieved chunks."""
    with create_custom_span(
        "re_rank_and_dedup",
        {"retrieval_count": len(state.get("retrieved_chunks", []))}
    ):
        chunks = state.get("retrieved_chunks", [])
        if not chunks:
            return state

        sorted_chunks = sorted(
            chunks,
            key=lambda chunk: chunk.get("similarity", 0.0),
            reverse=True,
        )

        seen_signatures = set()
        diversified: List[Dict[str, Any]] = []
        for chunk in sorted_chunks:
            signature = (chunk.get("section"), (chunk.get("content") or "")[:200])
            if signature in seen_signatures:
                continue
            seen_signatures.add(signature)
            diversified.append(chunk)

        state["retrieved_chunks"] = diversified
        state["retrieval_scores"] = [c.get("similarity", 0.0) for c in diversified]
        state.setdefault("analytics_metadata", {})["post_rank_count"] = len(diversified)

    return state


def validate_grounding(state: ConversationState, threshold: float = 0.45) -> ConversationState:
    """Ensure retrieval produced sufficiently similar chunks before generation."""
    scores = state.get("retrieval_scores", [])
    top_score = max(scores) if scores else 0.0

    status = "ok"
    if not scores:
        status = "no_results"
    elif top_score < threshold:
        status = "insufficient"

    state["grounding_status"] = status
    state.setdefault("analytics_metadata", {})["top_similarity"] = round(top_score, 3)

    if status != "ok":
        state["clarification_needed"] = True
        state["clarifying_question"] = (
            "I want to keep this grounded. Could you share a bit more detail so I can "
            "search the right knowledge?"
        )
    else:
        state["clarification_needed"] = False

    return state


def handle_grounding_gap(state: ConversationState) -> ConversationState:
    """Respond gracefully when grounding is insufficient."""
    if state.get("grounding_status") == "ok":
        return state

    message = (
        "I could not find context precise enough to stay factual yet. "
        "Tell me a little more about what you want to explore and I will pull "
        "the exact architecture notes or data you need."
    )

    with create_custom_span("grounding_gap_response", {"status": state.get("grounding_status")}):
        state["answer"] = message
        state["pipeline_halt"] = True

    return state


def generate_draft(state: ConversationState, rag_engine: RagEngine) -> Dict[str, Any]:
    """Generate a draft assistant response using retrieved context.

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
        logger.error("generate_draft called without query in state")
        raise KeyError("State must contain 'query' field for generation") from e

    # Access optional fields safely (Defensibility)
    retrieved_chunks = state.get("retrieved_chunks", [])
    role = state.get("role", "Just looking around")
    chat_history = state.get("chat_history", [])

    # Initialize update dict (Loose Coupling)
    update: Dict[str, Any] = {}
    state.setdefault("analytics_metadata", {})

    if state.get("pipeline_halt"):
        return state

    grounding_status = state.get("grounding_status")
    if grounding_status and grounding_status not in {"ok", "unknown"}:
        return state

    # For data display requests, we'll fetch live analytics later
    # Just set a placeholder for now
    if state.get("data_display_requested", False):
        placeholder = "Fetching live analytics data from Supabase..."
        update["answer"] = placeholder
        update["draft_answer"] = placeholder
        state.update(update)
        return state

    # RUNTIME AWARENESS: Detect technical deep dive requests (SOFTWARE DEVELOPER ONLY)
    # Based on PORTFOLIA_LANGGRAPH_CONTEXT.md - Section: "When User Asks Technical Questions"
    runtime_awareness_triggered = False
    runtime_content_block = None

    if role == "Software Developer":
        query_lower = query.lower()

        # Architecture questions → Show conversation flow diagram or full stack
        if any(kw in query_lower for kw in ["architecture", "how do you work", "how does this work", "system design", "how are you built"]):
            if "rag" in query_lower or "retrieval" in query_lower or "search" in query_lower:
                # RAG-specific architecture
                runtime_content_block = content_blocks.rag_pipeline_explanation()
                runtime_awareness_triggered = True
                logger.info("Runtime awareness: RAG pipeline explanation triggered")
            elif "flow" in query_lower or "pipeline" in query_lower or "nodes" in query_lower:
                # Conversation flow
                runtime_content_block = content_blocks.conversation_flow_diagram()
                runtime_awareness_triggered = True
                logger.info("Runtime awareness: Conversation flow diagram triggered")
            else:
                # General architecture
                runtime_content_block = content_blocks.architecture_stack_explanation()
                runtime_awareness_triggered = True
                logger.info("Runtime awareness: Architecture stack explanation triggered")

        # Performance questions → Show metrics table
        elif any(kw in query_lower for kw in ["performance", "latency", "speed", "how fast", "metrics", "p95", "p99"]):
            runtime_content_block = content_blocks.performance_metrics_table()
            runtime_awareness_triggered = True
            logger.info("Runtime awareness: Performance metrics table triggered")

        # Code questions → Show actual retrieval code
        elif any(kw in query_lower for kw in ["show me code", "show code", "show me the code", "retrieval code", "how do you retrieve"]):
            runtime_content_block = content_blocks.code_example_retrieval_method()
            runtime_awareness_triggered = True
            logger.info("Runtime awareness: Code example triggered")

        # SQL/query questions → Show pgvector query
        elif any(kw in query_lower for kw in ["sql", "query", "vector search", "pgvector", "how do you search"]):
            runtime_content_block = content_blocks.pgvector_query_example()
            runtime_awareness_triggered = True
            logger.info("Runtime awareness: pgvector query example triggered")

        # Cost questions → Show cost analysis
        elif any(kw in query_lower for kw in ["cost", "expensive", "pricing", "how much", "budget"]):
            runtime_content_block = content_blocks.cost_analysis_table()
            runtime_awareness_triggered = True
            logger.info("Runtime awareness: Cost analysis table triggered")

        # Scaling questions → Show enterprise scaling strategy
        elif any(kw in query_lower for kw in ["scale", "scaling", "enterprise", "100k users", "production", "deployment"]):
            runtime_content_block = content_blocks.enterprise_scaling_strategy()
            runtime_awareness_triggered = True
            logger.info("Runtime awareness: Enterprise scaling strategy triggered")

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

    # Runtime awareness: Add content block to context if triggered
    if runtime_awareness_triggered and runtime_content_block:
        extra_instructions.append(
            f"RUNTIME AWARENESS: The user asked a technical question about Portfolia's architecture/performance. "
            f"Below is a self-referential teaching block showing live data. Reference this in your explanation, "
            f"weave it into your narrative naturally, and expand on it conversationally. "
            f"Maintain warmth and curiosity while being technically precise.\n\n{runtime_content_block}"
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

    cleaned_answer = sanitize_generated_answer(answer)
    update["draft_answer"] = cleaned_answer
    update["answer"] = cleaned_answer

    # Update state in-place (current functional pipeline pattern)
    state.update(update)
    return state


def hallucination_check(state: ConversationState) -> ConversationState:
    """Attach lightweight citations and flag hallucination risk."""
    draft = state.get("draft_answer")
    chunks = state.get("retrieved_chunks", [])

    if not draft or not chunks:
        state["hallucination_safe"] = False if not chunks else state.get("hallucination_safe", True)
        return state

    citations = []
    for idx, chunk in enumerate(chunks, start=1):
        section = chunk.get("section") or f"knowledge chunk {idx}"
        citations.append(f"{idx}. {section}")

    citation_text = "; ".join(citations[:3])
    if citation_text and "Sources:" not in draft:
        state["draft_answer"] = f"{draft}\n\nSources: {citation_text}"

    state["hallucination_safe"] = True
    return state


def _split_answer_and_sources(answer: str) -> tuple[str, str]:
    if "Sources:" in answer:
        parts = answer.split("Sources:", 1)
        body = parts[0].strip()
        sources = parts[1].strip()
        return body, sources
    return answer.strip(), ""


def _summarize_answer(text: str, depth: int) -> List[str]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    limit = 2 if depth <= 1 else 3
    summary = []
    for sentence in sentences:
        if sentence.lower().startswith("sources:"):
            continue
        summary.append(f"- {sentence}")
        if len(summary) >= limit:
            break
    return summary


def _build_followups(variant: str) -> List[str]:
    if variant == "engineering":
        return [
            "Walk through the LangGraph node transitions",
            "Inspect the pgvector retrieval implementation",
            "Map this pattern onto your stack",
        ]
    if variant == "business":
        return [
            "Review the rollout checklist for enterprise teams",
            "Estimate cost savings for your workflow",
            "Explore adoption risks and mitigation steps",
        ]
    return [
        "See how the architecture adapts to customer support",
        "Peek at the analytics dashboard",
        "Ask for the testing and QA strategy",
    ]


def format_answer(state: ConversationState, rag_engine: RagEngine) -> Dict[str, Any]:
    """Structure the draft answer using headings, bullets, and toggles."""

    base_answer = state.get("draft_answer") or state.get("answer")
    if base_answer is None:
        logger.warning("format_answer called without draft_answer or answer - pipeline may have halted early")
        # Return empty dict to allow pipeline to continue gracefully
        return {}

    if not base_answer:
        return {}

    depth = state.get("depth_level", 1)
    layout_variant = state.get("layout_variant", "mixed")
    pending_actions = state.get("pending_actions", [])
    action_types = {action["type"] for action in pending_actions}
    query = state.get("query", "")
    role = state.get("role", "Just looking around")

    body_text, sources_text = _split_answer_and_sources(base_answer)
    summary_lines = _summarize_answer(body_text, depth)

    sections: List[str] = []
    sections.append("**Teaching Takeaways**")
    sections.extend(summary_lines or ["- I pulled the relevant context and kept the answer grounded."])

    details_block = content_blocks.render_block(
        "Full Walkthrough",
        body_text,
        summary="Expand for the detailed explanation",
        open_by_default=depth >= 2,
    )
    sections.append("")
    sections.append(details_block)

    if "render_live_analytics" in action_types:
        try:
            import requests
            from src.config.supabase_config import supabase_settings
            if supabase_settings.is_vercel:
                analytics_url = "https://noahsaiassistant.vercel.app/api/analytics"
            else:
                analytics_url = "http://localhost:3000/api/analytics"

            response = requests.get(analytics_url, timeout=3)
            response.raise_for_status()
            analytics_data = response.json()
            from src.flows.analytics_renderer import render_live_analytics

            analytics_report = render_live_analytics(analytics_data, state.get("role"), focus=None)
            sections.append("")
            sections.append(
                content_blocks.render_block(
                    "Live Analytics Snapshot",
                    analytics_report,
                    summary="View Supabase analytics",
                    open_by_default=depth >= 3,
                )
            )
        except Exception as exc:
            logger.error(f"Failed to fetch live analytics: {exc}")
            sections.append("")
            sections.append("Live analytics are temporarily unavailable. I can share the cached summary if you like.")

    if "include_metrics_block" in action_types:
        metrics, source = content_blocks.cost_latency_grounded_block()
        metrics_body = list(metrics) + [f"Source: {source}"]
        sections.append("")
        sections.append(
            content_blocks.render_block(
                "Cost · Latency · Grounding",
                metrics_body,
                summary="Metrics snapshot",
                open_by_default=depth >= 3,
            )
        )

    if "include_sequence_diagram" in action_types:
        sections.append("")
        sections.append(
            content_blocks.render_block(
                "Engineering Sequence",
                content_blocks.engineering_sequence_diagram(),
                summary="See the LangGraph handoff",
                open_by_default=depth >= 2,
            )
        )

    if "include_adaptation_diagram" in action_types:
        sections.append("")
        sections.append(
            content_blocks.render_block(
                "Enterprise Adaptation",
                content_blocks.enterprise_adaptation_diagram(),
                summary="Show the adaptation map",
                open_by_default=False,
            )
        )

    if "include_code_reference" in action_types:
        try:
            results = rag_engine.retrieve_with_code(query, role=role)
            snippets = results.get("code_snippets", []) if results else []
        except Exception as exc:
            logger.warning(f"Code retrieval failed: {exc}")
            snippets = []

        if snippets:
            snippet = snippets[0]
            code_content = snippet.get("content", "")
            citation = snippet.get("citation", "codebase")
            if is_valid_code_snippet(code_content):
                formatted_code = content_blocks.format_code_snippet(
                    code=code_content,
                    file_path=citation,
                    language="python",
                    description="Core logic referenced in this explanation",
                )
                sections.append("")
                sections.append(
                    content_blocks.render_block(
                        "Code Reference",
                        formatted_code,
                        summary="Peek at the implementation",
                        open_by_default=depth >= 3,
                    )
                )
                sections.append(content_blocks.code_display_guardrails())
        elif "include_code_reference" in action_types:
            sections.append("")
            sections.append("Code index is refreshing; happy to walk through the architecture instead.")

    if "explain_imports" in action_types:
        import_name = detect_import_in_query(query)
        if import_name:
            explanation_data = get_import_explanation(import_name, role)
            if explanation_data:
                formatted = content_blocks.format_import_explanation(
                    import_name=explanation_data["import"],
                    tier=explanation_data["tier"],
                    explanation=explanation_data["explanation"],
                    enterprise_concern=explanation_data.get("enterprise_concern", ""),
                    enterprise_alternative=explanation_data.get("enterprise_alternative", ""),
                    when_to_switch=explanation_data.get("when_to_switch", ""),
                )
                sections.append("")
                sections.append(
                    content_blocks.render_block(
                        f"Why {import_name}",
                        formatted,
                        summary=f"Stack choice: {import_name}",
                        open_by_default=False,
                    )
                )
        else:
            relevant_imports = search_import_explanations(query, role, top_k=3)
            if relevant_imports:
                bullets = []
                for imp_data in relevant_imports:
                    bullets.append(
                        f"{imp_data['import']}: {imp_data['explanation']}"
                    )
                sections.append("")
                sections.append(
                    content_blocks.render_block(
                        "Stack Justifications",
                        bullets,
                        summary="Why these libraries?",
                        open_by_default=False,
                    )
                )

    if "share_fun_facts" in action_types:
        sections.append("")
        fun_fact_lines = [
            line.lstrip("- ").strip()
            for line in content_blocks.fun_facts_block().split("\n")
            if line.strip()
        ]
        sections.append(
            content_blocks.render_block(
                "Fun Facts",
                fun_fact_lines,
                summary="Quick facts about Noah",
                open_by_default=False,
            )
        )

    if "share_mma_link" in action_types or state.get("query_type") == "mma":
        sections.append("")
        sections.append(content_blocks.mma_fight_link())

    if "send_linkedin" in action_types:
        sections.append("")
        sections.append(f"LinkedIn profile: {LINKEDIN_URL}")

    if "send_resume" in action_types:
        resume_link = state.get("resume_signed_url", RESUME_DOWNLOAD_URL)
        sections.append("")
        sections.append(f"Résumé download: {resume_link}")

    if "offer_resume_prompt" in action_types and not state.get("offer_sent"):
        sections.append("")
        sections.append("If it would help, I can share Noah's résumé or LinkedIn—just let me know.")

    if "ask_reach_out" in action_types:
        sections.append("")
        sections.append("Would you like Noah to reach out directly?")

    if "collect_confession" in action_types:
        sections.append("")
        sections.append(
            "💌 Your message is safe. Share it anonymously or add contact info and I'll pass it privately to Noah."
        )

    if sources_text:
        sections.append("")
        sections.append(
            content_blocks.render_block(
                "Sources",
                [line.strip() for line in sources_text.splitlines() if line.strip()],
                summary="Show citations",
                open_by_default=False,
            )
        )

    followups = _build_followups(state.get("followup_variant", "mixed"))
    sections.append("")
    sections.append("**Where next?**")
    sections.extend(f"- {item}" for item in followups)
    state["followup_prompts"] = followups

    enriched_answer = "\n".join(section for section in sections if section is not None)
    state["answer"] = enriched_answer.strip()
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

        if message_id and state.get("retrieved_chunks"):
            topk_ids = [chunk.get("id") for chunk in state["retrieved_chunks"] if chunk.get("id")]
            scores = state.get("retrieval_scores", [])
            retrieval_log = RetrievalLogData(
                message_id=message_id,
                topk_ids=topk_ids,
                scores=scores,
                grounded=state.get("grounding_status") == "ok",
            )
            supabase_analytics.log_retrieval(retrieval_log)
    except Exception as exc:
        logger.error("Failed logging analytics: %s", exc)
        if "analytics_metadata" not in state:
            state["analytics_metadata"] = {}
        state["analytics_metadata"]["logged_at"] = False

    # Note: update dict no longer needed since we write directly to state
    # When we migrate to LangGraph StateGraph, this will return partial dict only
    return state


def suggest_followups(state: ConversationState) -> ConversationState:
    """Generate curiosity-driven follow-up prompts."""
    if state.get("followup_prompts"):
        return state
    intent = state.get("query_intent") or state.get("query_type") or "general"
    role_mode = state.get("role_mode", "explorer")

    suggestions: List[str] = []
    if intent in {"technical", "engineering", "technical"}:
        suggestions = [
            "Want me to walk through the LangGraph node transitions in detail?",
            "Curious how the Supabase pgvector query works under load?",
            "Should we map this architecture to your internal stack?",
        ]
    elif intent in {"data", "analytics"}:
        suggestions = [
            "Need the retrieval accuracy metrics for last week?",
            "Want the cost-per-query breakdown?",
            "Should we compare grounding confidence across roles?",
        ]
    elif intent in {"career", "general"}:
        suggestions = [
            "Want the story behind building this assistant end to end?",
            "Should I outline Noah's production launch checklist?",
            "Curious how this adapts to your team's workflow?",
        ]

    if role_mode == "confession":
        suggestions = []  # Confession mode stays focused on the message

    if suggestions:
        state["followup_prompts"] = suggestions
        followup_lines = "\n".join(f"- {item}" for item in suggestions)
        existing_answer = state.get("answer") or ""
        state["answer"] = (
            f"{existing_answer}\n\nNext directions I can cover:\n{followup_lines}"
            if existing_answer
            else f"Next directions I can cover:\n{followup_lines}"
        )

    return state


def update_memory(state: ConversationState) -> ConversationState:
    """Store soft signals in session memory for future turns."""
    memory = state.setdefault("session_memory", {})
    topics = memory.setdefault("topics", [])
    intent = state.get("query_intent")
    if intent and intent not in topics:
        topics.append(intent)

    entities = state.get("entities", {})
    if entities:
        stored_entities = memory.setdefault("entities", {})
        for key, value in entities.items():
            if value and key not in stored_entities:
                stored_entities[key] = value

    memory["last_grounding_status"] = state.get("grounding_status")

    return state


# ---------------------------------------------------------------------------
# Backward-compatible wrappers (tests and legacy modules)
# ---------------------------------------------------------------------------


def generate_answer(state: ConversationState, rag_engine: RagEngine) -> Dict[str, Any]:
    """Backward-compatible alias for generate_draft."""
    return generate_draft(state, rag_engine)


def apply_role_context(state: ConversationState, rag_engine: RagEngine) -> Dict[str, Any]:
    """Backward-compatible alias for format_answer."""
    return format_answer(state, rag_engine)
