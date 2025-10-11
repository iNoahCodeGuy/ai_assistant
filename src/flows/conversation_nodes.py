"""Composable conversation nodes for the LangGraph migration path."""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict

from src.flows.conversation_state import ConversationState
from src.core.rag_engine import RagEngine
from src.analytics.supabase_analytics import supabase_analytics, UserInteractionData
from src.config.supabase_config import supabase_settings
from src.services.resend_service import get_resend_service
from src.services.storage_service import get_storage_service
from src.services.twilio_service import get_twilio_service

logger = logging.getLogger(__name__)

RESUME_DOWNLOAD_URL = os.getenv("RESUME_DOWNLOAD_URL", "https://example.com/noah-resume.pdf")
LINKEDIN_URL = os.getenv("LINKEDIN_URL", "https://linkedin.com/in/noahdelacalzada")


def classify_query(state: ConversationState) -> ConversationState:
    """Classify the incoming query and stash the result on state."""
    lowered = state.query.lower()
    if any(re.search(r"\\b" + k + r"\\b", lowered) for k in ["mma", "fight", "ufc", "bout", "cage"]):
        state.stash("query_type", "mma")
    elif any(term in lowered for term in ["fun fact", "hobby", "interesting fact", "hot dog"]):
        state.stash("query_type", "fun")
    elif any(term in lowered for term in ["code", "technical", "stack", "architecture", "implementation", "retrieval"]):
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
    """Generate an assistant response using retrieved context."""
    answer = rag_engine.response_generator.generate_basic_response(
        state.query,
        fallback_docs=state.fetch("retrieval_matches", []),
        chat_history=state.chat_history
    )
    state.set_answer(answer)
    return state


def plan_actions(state: ConversationState) -> ConversationState:
    """Derive follow-up actions (resume offers, tables, notifications)."""
    state.pending_actions.clear()
    query_type = state.fetch("query_type", "general")
    lowered = state.query.lower()
    user_turns = sum(1 for message in state.chat_history if message.get("role") == "user")

    def add_action(action_type: str, **extras: Any) -> None:
        state.append_pending_action({"type": action_type, **extras})

    resume_requested = any(key in lowered for key in ["send resume", "email resume", "resume", "cv"])
    linkedin_requested = any(key in lowered for key in ["linkedin", "link me", "profile"])
    contact_requested = any(key in lowered for key in ["reach out", "contact me", "call me", "follow up"])

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

    if state.role == "Hiring Manager (nontechnical)":
        if not resume_requested and not linkedin_requested and user_turns >= 2:
            add_action("offer_resume_prompt")
    elif state.role == "Hiring Manager (technical)":
        if query_type == "technical":
            add_action("include_architecture_overview")
            add_action("provide_data_tables")
            add_action("explain_enterprise_usage")
        if not resume_requested and not linkedin_requested and user_turns >= 2:
            add_action("offer_resume_prompt")
    elif state.role == "Software Developer":
        if query_type == "technical":
            add_action("include_code_snippets")
            add_action("provide_data_tables")
            add_action("explain_stack_currency")
    elif state.role == "Just looking around":
        if query_type == "mma":
            add_action("share_mma_link")
        else:
            add_action("share_fun_facts")
    elif state.role == "Looking to confess crush":
        add_action("collect_confession")

    return state


def _data_collection_table() -> str:
    return (
        "| Dataset | Purpose | Capture | Notes |\n"
        "| --- | --- | --- | --- |\n"
        "| messages | Conversation transcripts | query, answer, latency, tokens | Drives feedback + analytics |\n"
        "| retrieval_logs | Retrieved KB chunks | chunk_ids, scores, grounded | Evaluates retrieval quality |\n"
        "| feedback | Ratings & comments | rating, comment, email opt-in | Triggers outreach + improvements |\n"
        "| links | Resource shortcuts | resume, linkedin, github URLs | Used by resume/link offers |\n"
        "| confessions | Anonymous messages | name, contact, message, anonymity | Powers Confess role alerts |"
    )


def _fun_facts_block() -> str:
    return (
        "- Noah competed in 10 MMA fights (8 amateur including two title bouts, 2 professional).\n"
        "- He once ate 10 hot dogs in under eight minutes during a charity challenge.\n"
        "- Outside of tech he loves chess puzzles and coaching youth wrestling."
    )


def apply_role_context(state: ConversationState, rag_engine: RagEngine) -> ConversationState:
    """Tailor the generated answer with role-specific enrichments."""
    if not state.answer:
        return state

    components = [state.answer]
    actions = {action["type"] for action in state.pending_actions}
    query_type = state.fetch("query_type", "general")

    if "provide_data_tables" in actions:
        components.append("\n\n### 📊 Data Collection Overview\n" + _data_collection_table())

    if "include_architecture_overview" in actions:
        components.append(
            "\n\n### 🏗️ Architecture Snapshot\n"
            "- Frontend: Next.js on Vercel with role-aware chat UI.\n"
            "- Backend: Vercel serverless functions orchestrating RAG + actions.\n"
            "- Retrieval: Supabase Postgres with pgvector embeddings.\n"
            "- Actions: Resend for email, Twilio for SMS notifications, Supabase logging for analytics."
        )

    if "explain_enterprise_usage" in actions:
        components.append(
            "\n\n### 🏢 Enterprise Fit\n"
            "A role router lets a company like Acme Corp route each query to the right compliance-approved persona, "
            "enabling audit trails, targeted tooling, and the ability to plug in managed vector DBs or queues as volume grows."
        )

    if "explain_stack_currency" in actions:
        components.append(
            "\n\n### 🔄 Staying Current\n"
            "Every deploy updates Supabase KB entries and code index snapshots so responses always reflect the "
            "data_collection_management branch. LangSmith traces verify new features before release."
        )

    if "share_fun_facts" in actions:
        components.append("\n\n### 🎉 Fun Facts\n" + _fun_facts_block())

    if "share_mma_link" in actions or query_type == "mma":
        components.append(f"\n\nWatch Noah's featured fight: {supabase_settings.youtube_fight_link}")

    if "send_linkedin" in actions:
        components.append(f"\n\nHere is Noah's LinkedIn profile: {LINKEDIN_URL}")
        state.stash("offer_sent", True)

    if "send_resume" in actions:
        resume_link = state.fetch("resume_signed_url", RESUME_DOWNLOAD_URL)
        components.append(f"\n\nDownload Noah's resume: {resume_link}")
        state.stash("offer_sent", True)

    if "include_code_snippets" in actions:
        try:
            results = rag_engine.retrieve_with_code(state.query, role=state.role)
            snippets = results.get("code_snippets", []) if results else []
        except Exception:  # pragma: no cover - defensive guard
            snippets = []
        if snippets:
            snippet = snippets[0]
            components.append(
                "\n\n```python\n" + snippet.get("content", "") + "\n```\n"
                f"Source: {snippet.get('citation', 'codebase')}"
            )

    if "offer_resume_prompt" in actions and not state.fetch("offer_sent"):
        components.append("\n\nWould you like me to email you my resume or share my LinkedIn profile?")

    if "ask_reach_out" in actions:
        components.append("\n\nWould you like Noah to reach out?")

    if "collect_confession" in actions:
        components.append(
            "\n\n💌 Your message is safe. You can submit anonymously or include your name and contact info, and I’ll pass it along with a private SMS to Noah."
        )

    state.set_answer("".join(components))
    return state


def execute_actions(state: ConversationState) -> ConversationState:
    """Perform side effects like sending emails or SMS notifications."""
    if not state.pending_actions:
        return state

    resend_service = None
    storage_service = None
    twilio_service = None

    def ensure_resend():
        nonlocal resend_service
        if resend_service is None:
            try:
                resend_service = get_resend_service()
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.error("Failed to initialize Resend service: %s", exc)
                resend_service = False
        return resend_service

    def ensure_storage():
        nonlocal storage_service
        if storage_service is None:
            try:
                storage_service = get_storage_service()
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.error("Failed to initialize Storage service: %s", exc)
                storage_service = False
        return storage_service

    def ensure_twilio():
        nonlocal twilio_service
        if twilio_service is None:
            try:
                twilio_service = get_twilio_service()
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.error("Failed to initialize Twilio service: %s", exc)
                twilio_service = False
        return twilio_service

    contact_name = state.fetch("user_name", "there")
    contact_email = state.fetch("user_email")
    contact_phone = state.fetch("user_phone")
    message_preview = state.query[:120]

    for action in state.pending_actions:
        action_type = action.get("type")

        try:
            if action_type == "send_resume":
                recipient_email = action.get("email") or contact_email
                recipient_name = action.get("name") or contact_name
                if not recipient_email:
                    logger.info("Skipping resume send; no email available")
                    continue

                resume_url = state.fetch("resume_signed_url")
                if not resume_url:
                    service = ensure_storage()
                    if not service:
                        continue
                    resume_path = action.get("resume_path", "resumes/noah_resume.pdf")
                    expires_in = action.get("expires_in", 86400)
                    resume_url = service.get_signed_url(resume_path, expires_in=expires_in)
                    state.stash("resume_signed_url", resume_url)

                service = ensure_resend()
                if not service:
                    continue
                response = service.send_resume_email(
                    to_email=recipient_email,
                    to_name=recipient_name,
                    resume_url=resume_url,
                    message=action.get("message")
                )
                state.update_analytics("resume_email_status", response.get("status", "unknown"))

            elif action_type == "notify_resume_sent":
                service = ensure_twilio()
                if not service:
                    continue
                service.send_contact_alert(
                    from_name="Resume Bot",
                    from_email="assistant@noahdelacalzada.com",
                    message_preview=f"Resume dispatched to {contact_email or 'recipient'}."
                )

            elif action_type == "notify_contact_request":
                service = ensure_resend()
                if service and contact_email:
                    service.send_contact_notification(
                        from_name=contact_name,
                        from_email=contact_email,
                        message=state.query,
                        user_role=state.role,
                        phone=contact_phone,
                    )

                twilio = ensure_twilio()
                if twilio:
                    twilio.send_contact_alert(
                        from_name=contact_name,
                        from_email=contact_email or "unknown@contact.com",
                        message_preview=message_preview,
                        is_urgent=action.get("urgent", False)
                    )

            elif action_type == "send_linkedin":
                state.update_analytics("linkedin_offer", True)

        except Exception as exc:  # pragma: no cover - defensive guard
            logger.error("Action %s failed: %s", action_type, exc)

    return state

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
