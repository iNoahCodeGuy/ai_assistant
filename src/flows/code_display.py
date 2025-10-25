"""Self-code display helper for Portfolia responses.

This module centralizes logic used when the user explicitly asks to see how
Portfolia implements a particular capability. It maps friendly query phrases
(e.g. "how do you retrieve documents?") to concrete source files and symbols,
loads the relevant snippet, and formats it for downstream presentation logic.

The helper purposely keeps the registry compact and curated so we only expose
core modules that are safe to surface in marketing conversations. Each entry
includes:
    - file_path: path to the source file relative to the repo root
    - description: short human-readable summary for the block header
    - keywords: lower-case triggers that map user phrasing to this module
    - hotspots: mapping of phrase -> symbol for more precise extraction
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from src.state.conversation_state import ConversationState
from src.flows import content_blocks


@dataclass(frozen=True)
class ModuleMetadata:
    """Metadata describing a source module that can be surfaced."""

    file_path: str
    description: str
    keywords: Sequence[str]
    hotspots: Sequence[tuple[str, str]]
    language: str = "python"
    max_lines: int = 80


_REPO_ROOT = Path(__file__).resolve().parents[2]

_MODULE_REGISTRY: Dict[str, ModuleMetadata] = {
    "rag_engine": ModuleMetadata(
        file_path="src/core/rag_engine.py",
        description="RAG engine: pgvector retrieval + guided generation",
        keywords=("rag", "retrieval", "pgvector", "grounding"),
        hotspots=(
            ("retrieve", "retrieve"),
            ("ground", "validate_grounding"),
            ("plan", "_plan_response"),
        ),
    ),
    "core_nodes": ModuleMetadata(
        file_path="src/flows/core_nodes.py",
        description="Core LangGraph nodes orchestrating each turn",
        keywords=("orchestrate", "pipeline", "node", "format", "presentation"),
        hotspots=(
            ("format", "format_answer"),
            ("analytics", "_attach_analytics"),
            ("follow up", "suggest_followups"),
        ),
    ),
    "presentation_control": ModuleMetadata(
        file_path="src/flows/presentation_control.py",
        description="Presentation control: depth + layout heuristics",
        keywords=("depth", "presentation", "layout", "toggle"),
        hotspots=(
            ("depth", "depth_controller"),
            ("display", "display_controller"),
        ),
    ),
    "pgvector_retriever": ModuleMetadata(
        file_path="src/retrieval/pgvector_retriever.py",
        description="Supabase pgvector retriever wrapper",
        keywords=("pgvector", "supabase", "vector"),
        hotspots=(("retrieve", "retrieve"),),
        max_lines=70,
    ),
}


def detect_requested_modules(query: str) -> List[str]:
    """Return registry keys matched by the user's query text.

    Requires explicit implementation intent so we do not trigger on every
    conceptual architecture question. Keywords like "show", "code", or
    "how do you" gate the detection and module keywords refine the match.
    """

    lowered = query.lower()
    gating_tokens = (
        "show me",
        "show the",
        "display",
        "code",
        "implementation",
        "snippet",
        "source",
        "under the hood",
        "walk me",
        "how do you",
        "how does",
    )

    if not any(token in lowered for token in gating_tokens):
        return []

    matches: List[str] = []
    for key, meta in _MODULE_REGISTRY.items():
        if any(token in lowered for token in meta.keywords):
            matches.append(key)
    # Fallback: generic "show your code" request defaults to core nodes
    if not matches and "code" in lowered:
        matches.append("core_nodes")
    return matches


def _extract_symbol_snippet(file_path: Path, symbol: str, max_lines: int) -> Optional[str]:
    """Return a code excerpt centered around the requested symbol."""

    try:
        contents = file_path.read_text().splitlines()
    except FileNotFoundError:
        return None

    start_idx = None
    indent = None
    for idx, line in enumerate(contents):
        if line.strip().startswith("def ") or line.strip().startswith("class "):
            current_symbol = line.strip().split()[1].split("(")[0].split(":")[0]
            if current_symbol == symbol:
                start_idx = idx
                indent = len(line) - len(line.lstrip(" "))
                break
    if start_idx is None:
        return None

    snippet: List[str] = []
    for line in contents[start_idx:]:
        snippet.append(line)
        if line.strip() == "":
            continue
        # Stop when indentation returns to the outer scope
        current_indent = len(line) - len(line.lstrip(" "))
        if current_indent <= (indent or 0) and line.strip() and len(snippet) > 1:
            break
        if len(snippet) >= max_lines:
            break
    return "\n".join(snippet).rstrip()


def _fallback_snippet(file_path: Path, max_lines: int) -> Optional[str]:
    try:
        contents = file_path.read_text().splitlines()
    except FileNotFoundError:
        return None
    return "\n".join(contents[: max_lines or 60]).rstrip()


def _match_symbol(query: str, metadata: ModuleMetadata) -> Optional[str]:
    lowered = query.lower()
    for trigger, symbol in metadata.hotspots:
        if trigger in lowered:
            return symbol
    return metadata.hotspots[0][1] if metadata.hotspots else None


def _load_snippet(module_key: str, query: str) -> Optional[Dict[str, str]]:
    metadata = _MODULE_REGISTRY.get(module_key)
    if not metadata:
        return None

    file_path = (_REPO_ROOT / metadata.file_path).resolve()
    symbol = _match_symbol(query, metadata)
    snippet: Optional[str] = None
    if symbol:
        snippet = _extract_symbol_snippet(file_path, symbol, metadata.max_lines)
    if not snippet:
        snippet = _fallback_snippet(file_path, metadata.max_lines)
    if not snippet:
        return None

    return {
        "module": module_key,
        "file_path": metadata.file_path,
        "code": snippet,
        "language": metadata.language,
        "description": metadata.description,
    }


def get_self_code_snippets(state: ConversationState, max_modules: int = 2) -> List[Dict[str, str]]:
    """Return formatted code snippets for inclusion in the response.

    The caller is expected to respect presentation toggles; this helper provides a
    simple guard as well. Returned dictionaries contain keys: title, body,
    summary, and module.
    """

    if not state.get("self_code_requested"):
        return []

    display_toggles = state.get("display_toggles", {})
    if not display_toggles.get("code", False):
        return []

    query = state.get("query", "")
    requested = state.get("requested_code_modules") or []
    if not requested:
        requested = detect_requested_modules(query)
    # Deduplicate while preserving order
    seen: set[str] = set()
    ordered = []
    for module in requested:
        if module in _MODULE_REGISTRY and module not in seen:
            ordered.append(module)
            seen.add(module)
    if not ordered:
        return []

    snippets: List[Dict[str, str]] = []
    for module in ordered[:max_modules]:
        loaded = _load_snippet(module, query)
        if not loaded:
            continue
        formatted = content_blocks.format_code_snippet(
            loaded["code"], language=loaded["language"], file_path=loaded["file_path"]
        )
        snippets.append(
            {
                "module": module,
                "title": loaded["description"],
                "body": formatted,
                "summary": f"Direct excerpt from {loaded['file_path']}",
            }
        )
    return snippets


def list_supported_modules() -> Iterable[str]:
    """Expose supported module keys for testing/documentation."""

    return _MODULE_REGISTRY.keys()
