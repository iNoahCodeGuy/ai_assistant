"""Content block generators for enterprise-focused conversation responses.

This module provides reusable content blocks that explain the product's purpose,
architecture, data strategy, and enterprise adaptability to technical stakeholders.
Each block is designed to be concise, informative, and impressive to both junior
and senior developers evaluating Noah's skills.
"""

from src.config.supabase_config import supabase_settings


def format_section(title: str, body: str, *, include_divider: bool = True) -> str:
    """Format a section with a divider and level-three heading.

    Args:
        title: Section title to render as heading
        body: Markdown body content to follow the heading
        include_divider: Whether to prefix the section with a horizontal divider

    Returns:
        Markdown string containing the formatted section
    """
    parts = []
    if include_divider:
        parts.append("---")
    parts.append(f"### {title}")
    parts.append(body.strip())
    return "\n".join(parts)


def format_callout(message: str, *, label: str = "TIP") -> str:
    """Format a single-line callout block.

    Args:
        message: Main callout body text
        label: Short uppercase label to prefix the message with

    Returns:
        Markdown blockquote callout
    """
    return f"> {label}: {message.strip()}"


def data_collection_table() -> str:
    """Generate markdown table summarizing tracked datasets.

    Returns:
        Markdown table showing dataset names, purposes, captured fields, and notes.
    """
    return (
        "| Dataset | Purpose | Capture | Notes |\n"
        "| --- | --- | --- | --- |\n"
        "| messages | Conversation transcripts | query, answer, latency, tokens | Drives feedback + analytics |\n"
        "| retrieval_logs | Retrieved KB chunks | chunk_ids, scores, grounded | Evaluates retrieval quality |\n"
        "| feedback | Ratings & comments | rating, comment, email opt-in | Triggers outreach + improvements |\n"
        "| links | Resource shortcuts | resume, linkedin, github URLs | Used by resume/link offers |\n"
        "| confessions | Anonymous messages | name, contact, message, anonymity | Powers Confess role alerts |"
    )


def fun_facts_block() -> str:
    """Generate fun facts about Noah.

    Returns:
        Markdown list of interesting personal facts.
    """
    return (
        "- Noah competed in 10 MMA fights (8 amateur including two title bouts, 2 professional).\n"
        "- He once ate 10 hot dogs in under eight minutes during a charity challenge.\n"
        "- Outside of tech he loves chess puzzles and coaching youth wrestling."
    )


def purpose_block() -> str:
    """Generate product purpose statement for enterprise evaluators.

    Returns:
        Markdown list explaining mission, enterprise signal, and outcome.
    """
    return (
        "- Mission: Provide a role-aware assistant that answers complex questions with grounded citations.\n"
        "- Enterprise Signal: Demonstrates Noah's ability to blend agentic tooling with RAG to solve business workflows.\n"
        "- Outcome: Faster decision support for teams evaluating policies, technical documentation, or customer scenarios."
    )


def data_strategy_block() -> str:
    """Generate data management strategy overview.

    Returns:
        Markdown list explaining vector store, pipelines, and analytics approach.
    """
    return (
        "- Vector Store: Supabase pgvector centralizes embeddings for consistent retrieval and SQL-governed auditing.\n"
        "- Pipelines: Deterministic migration scripts refresh embeddings on deploy so content stays versioned and reproducible.\n"
        "- Analytics: Supabase tables track messages, retrieval scores, and feedback to guide continuous improvement."
    )


def enterprise_adaptability_block() -> str:
    """Generate enterprise scaling and adaptation strategy.

    Returns:
        Markdown list covering infrastructure, security, and extensibility.
    """
    return (
        "- Infrastructure: Containerize the Vercel services or move into Kubernetes for regional redundancy and traffic shaping.\n"
        "- Security: Layer SSO, secrets management, and dedicated vector clusters to satisfy enterprise governance.\n"
        "- Extensibility: Swap action nodes to integrate ticketing, CRM, or observability stacks without rewriting the orchestration logic."
    )


def architecture_snapshot() -> str:
    """Generate architecture overview for technical stakeholders.

    Returns:
        Markdown list showing frontend, backend, retrieval, and action layers.
    """
    return (
        "- Frontend: Static Vercel site plus Streamlit demo surfaces for rapid iteration.\n"
        "- Backend: Python serverless functions coordinating LangGraph nodes and action services.\n"
        "- Retrieval: Supabase Postgres with pgvector embeddings for governed semantic search.\n"
        "- Actions: Resend email, Twilio SMS, and Supabase analytics nodes managed via service factories."
    )


def enterprise_fit_explanation() -> str:
    """Explain how the product fits enterprise use cases.

    Returns:
        Paragraph explaining role routing and scalability for major enterprises.
    """
    return (
        "A role router lets a major enterprise send each message to the right compliance-approved persona, "
        "keeping answers auditable while scaling to managed vector databases, event queues, and downstream systems."
    )


def stack_importance_explanation() -> str:
    """Explain the importance of each layer in the stack.

    Returns:
        Markdown list covering frontend, backend, retrieval/data, and observability layers.
    """
    return (
        "- Frontend (Static site + Streamlit): Keeps demos fast and controlled while providing patterns for an enterprise portal handoff.\n"
        "- Backend (Python serverless LangGraph nodes): Coordinates RAG flows and action services with guardrails that scale into microservices.\n"
        "- Retrieval & Data (Supabase Postgres + pgvector): Centralizes governed knowledge, enables SQL-grade auditing, and simplifies swapping in managed vector stores.\n"
        "- Observability & Models (LangSmith + compat layer): Guarantees traceability, regression testing, and future model agility without painful rewrites."
    )


def mma_fight_link() -> str:
    """Get Noah's featured MMA fight link.

    Returns:
        Formatted message with YouTube fight link.
    """
    return f"Watch Noah's featured fight: {supabase_settings.youtube_fight_link}"


def format_code_snippet(
    code: str,
    file_path: str,
    language: str = "python",
    description: str = "",
    branch: str = "main"
) -> str:
    """Format a code snippet with file path, description, and enterprise prompt.

    Args:
        code: The actual code content
        file_path: Relative path to the file (e.g., "src/core/retriever.py")
        language: Programming language for syntax highlighting
        description: Optional description of what the code does
        branch: Git branch name

    Returns:
        Formatted markdown code block with metadata
    """
    header = f"**File**: `{file_path}` @ `{branch}`"
    if description:
        header += f"\n**Purpose**: {description}"

    code_block = f"```{language}\n{code}\n```"

    footer = "\n> Would you like to see the enterprise variant, test coverage, or full file?"

    return f"{header}\n\n{code_block}{footer}"


def format_import_explanation(
    import_name: str,
    tier: str,
    explanation: str,
    enterprise_concern: str = "",
    enterprise_alternative: str = "",
    when_to_switch: str = ""
) -> str:
    """Format an import explanation with enterprise context.

    Args:
        import_name: Name of the import/library (e.g., "openai", "supabase")
        tier: Explanation tier (1, 2, or 3)
        explanation: Main explanation text
        enterprise_concern: Optional enterprise-level concerns
        enterprise_alternative: Optional enterprise replacement options
        when_to_switch: Optional guidance on when to switch

    Returns:
        Formatted markdown explanation
    """
    sections = [f"### 📦 {import_name.upper()}\n"]
    sections.append(explanation)

    if tier in ["2", "3"] and enterprise_concern:
        sections.append(f"\n**Enterprise Concerns**: {enterprise_concern}")

    if tier == "3" and enterprise_alternative:
        sections.append(f"\n**Enterprise Alternative**: {enterprise_alternative}")

    if tier == "3" and when_to_switch:
        sections.append(f"\n**When to Switch**: {when_to_switch}")

    return "\n".join(sections)


def code_display_guardrails() -> str:
    """Return standard code display guardrails message.

    Returns:
        Standard guardrails notice for code snippets
    """
    return (
        "\n---\n"
        "**Code Display Guardrails**: All sensitive values (API keys, tokens) are redacted. "
        "Snippets shown are 10-40 lines for clarity. Full implementation available on request."
    )


def qa_strategy_block() -> str:
    """Generate QA strategy overview for product/architecture questions.

    Returns:
        Markdown list explaining automated quality assurance approach.
    """
    return (
        "- Automated regression tests: 14 scenarios covering analytics display, prompt deduplication, "
        "professional formatting, and code validation (all passing in ~1.2s).\n"
        "- Pre-commit hooks block emoji headers, duplicate prompts, and raw data dumps before code lands.\n"
        "- CI/CD quality gates: GitHub Actions stop merges that violate conversation standards.\n"
        "- Production monitoring checks success rate, latency, and formatting compliance every day.\n"
        "- Documentation in `docs/QUALITY_ASSURANCE_STRATEGY.md` keeps the team aligned on quality.\n\n"
        "Net result: new features cannot break conversation quality without being caught immediately."
    )


def role_switch_suggestion(target_role: str) -> str:
    """Generate suggestion to switch roles for better answers.

    Args:
        target_role: Recommended role name (e.g., "Hiring Manager (technical)")

    Returns:
        Markdown suggestion to switch roles.
    """
    message = (
        f"Switch to the {target_role} role for deeper technical context—"
        "you'll see code snippets, architecture snapshots, and implementation details."
    )
    return "\n" + format_callout(message)


# ============================================================================
# INTELLIGENT RESUME DISTRIBUTION - SUBTLE AVAILABILITY MENTIONS (Mode 2)
# ============================================================================
# These functions generate natural, non-pushy availability mentions when
# hiring signals are detected. See docs/features/INTELLIGENT_RESUME_DISTRIBUTION.md
# and docs/context/CONVERSATION_PERSONALITY.md Section 6.1 for full specification.


def get_subtle_availability_mention(hiring_signals: list[str]) -> str:
    """Generate subtle availability mention based on detected hiring signals.

    This function creates ONE natural, non-pushy sentence that informs hiring
    managers Noah is available, but ONLY when they've already mentioned active
    hiring. The mention is designed to feel like an afterthought, not a pitch.

    Mode 2 Guardrails (from QA standards):
    - User-initiated interest: Only after user mentions hiring first
    - Once per conversation: Max 1 subtle mention
    - Education remains primary: ≥50% of response is educational
    - No aggressive CTAs: No "send email", "click here", "sign up"
    - Natural placement: At end of educational response

    Args:
        hiring_signals: List of detected signals (e.g., ["mentioned_hiring", "described_role"])

    Returns:
        Natural, single-sentence availability mention

    Examples:
        >>> get_subtle_availability_mention(["mentioned_hiring", "described_role"])
        "By the way, Noah's available for roles like this if you'd like to learn more about his experience."

        >>> get_subtle_availability_mention(["described_role", "team_context"])
        "Noah specializes in building production RAG systems—happy to share more if you're interested."
    """
    # Variation 1: General hiring mention
    if "mentioned_hiring" in hiring_signals and "described_role" in hiring_signals:
        return (
            "\n\nBy the way, Noah's available for roles like this if you'd like to "
            "learn more about his experience building production GenAI systems."
        )

    # Variation 2: Role-specific mention
    if "described_role" in hiring_signals:
        return (
            "\n\nNoah specializes in building production RAG systems and LLM orchestration—"
            "happy to share more about his experience if you're interested."
        )

    # Variation 3: Team context mentioned
    if "team_context" in hiring_signals and len(hiring_signals) >= 2:
        return (
            "\n\nIf your team is exploring GenAI applications, Noah's available to discuss "
            "how this architecture could adapt to your use case."
        )

    # Variation 4: Timeline/urgency mentioned
    if "asked_timeline" in hiring_signals:
        return (
            "\n\nNoah's currently available and could discuss timeline fit if you'd like to "
            "explore his background further."
        )

    # Variation 5: Default subtle mention (fallback)
    return (
        "\n\nBy the way, Noah's available for opportunities like this if you'd like to "
        "learn more about his work."
    )


def get_availability_with_context(hiring_signals: list[str], discussed_topic: str = "") -> str:
    """Generate context-aware availability mention tied to conversation topic.

    This variation customizes the mention based on what was just discussed,
    making it feel even more natural and relevant.

    Args:
        hiring_signals: List of detected signals
        discussed_topic: What the conversation was about (e.g., "RAG architecture", "vector search")

    Returns:
        Context-aware availability mention

    Examples:
        >>> get_availability_with_context(["mentioned_hiring"], "RAG architecture")
        "By the way, Noah's built several production RAG systems and is available to discuss
        how this architecture could work for your team."
    """
    if not discussed_topic:
        return get_subtle_availability_mention(hiring_signals)

    # Context-aware variations
    if "rag" in discussed_topic.lower():
        return (
            f"\n\nBy the way, Noah's built production RAG systems handling millions of queries—"
            "available to discuss how this could work for your use case if you're interested."
        )

    if "vector" in discussed_topic.lower() or "embedding" in discussed_topic.lower():
        return (
            f"\n\nNoah specializes in vector search optimization and pgvector implementations—"
            "happy to discuss his experience if you're exploring this for your team."
        )

    if "llm" in discussed_topic.lower() or "gpt" in discussed_topic.lower():
        return (
            f"\n\nNoah's worked extensively with LLM orchestration and prompt engineering—"
            "available to share insights if you're building similar systems."
        )

    # Default to standard mention
    return get_subtle_availability_mention(hiring_signals)


def format_availability_mention(mention: str) -> str:
    """Format availability mention with consistent styling.

    Ensures all mentions have proper spacing and non-pushy tone markers.

    Args:
        mention: Raw availability mention text

    Returns:
        Properly formatted mention with spacing
    """
    # Ensure double newline before mention (separates from educational content)
    if not mention.startswith("\n\n"):
        mention = "\n\n" + mention.lstrip()

    return mention.strip()
