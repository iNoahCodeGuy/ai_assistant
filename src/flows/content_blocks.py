"""Content block generators for enterprise-focused conversation responses.

This module provides reusable content blocks that explain the product's purpose,
architecture, data strategy, and enterprise adaptability to technical stakeholders.
Each block is designed to be concise, informative, and impressive to both junior
and senior developers evaluating Noah's skills.
"""

from src.config.supabase_config import supabase_settings


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
