# Role-Specific Behaviors

This guide reflects the LangGraph-style flow (`run_conversation_flow`) that now powers Noah's AI Assistant. Responses are composed by the node stack in `src/flows/conversation_nodes.py`, and each role toggles different pending actions inside `plan_actions`.

## Hiring Manager (nontechnical)
- Career-first tone using career knowledge base chunks.
- Automatically offers resume/LinkedIn after two user turns unless already shared.
- Includes business-focused bullet points and prompts for follow-up contact.

## Hiring Manager (technical)
- Combines career summary with architecture snapshot and data-table appendix when queries are technical.
- Can request signed resume link or LinkedIn; actions trigger Resend email and optional SMS notification.
- Highlights enterprise fit and stack freshness sections.

## Software Developer
- Prioritizes technical retrieval; `plan_actions` flags `include_code_snippets` when keywords show up.
- `apply_role_context` embeds the first retrieved code snippet (if available) in fenced code block format.
- Adds “Staying Current” note describing ongoing data refresh cadence.

## Just Looking Around
- Provides conversational overview plus fun facts block.
- MMA-oriented queries append the featured fight link from Supabase settings.
- Keeps tone light and avoids deep technical content unless explicitly requested.

## Looking to Confess Crush
- Bypasses LangGraph path; Streamlit form captures the message and stores it locally (`data/confessions.csv`).
- Conversations simply acknowledge the mode and direct users to the form.

## Shared Behaviors
- All LangGraph roles record analytics through `log_and_notify`, including query type, latency, and session metadata.
- Conversation state keeps recent chat history so `generate_answer` can reference prior turns.
- Pending actions drive contextual enrichments (`apply_role_context`) and side effects (`execute_actions`).

For a complete inventory of runtime modules, see `docs/runtime_dependencies.md`. This file supersedes older RoleRouter documentation.
