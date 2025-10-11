from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ConversationState:
    """Shared state container passed between conversation nodes."""

    role: str
    query: str
    chat_history: List[Dict[str, str]] = field(default_factory=list)
    retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    answer: Optional[str] = None
    pending_actions: List[Dict[str, Any]] = field(default_factory=list)
    analytics_metadata: Dict[str, Any] = field(default_factory=dict)
    extras: Dict[str, Any] = field(default_factory=dict)

    def append_pending_action(self, action: Dict[str, Any]) -> None:
        self.pending_actions.append(action)

    def set_answer(self, response: str) -> None:
        self.answer = response

    def add_retrieved_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        if not chunks:
            return
        self.retrieved_chunks.extend(chunks)

    def update_analytics(self, key: str, value: Any) -> None:
        self.analytics_metadata[key] = value

    def stash(self, key: str, value: Any) -> None:
        self.extras[key] = value

    def fetch(self, key: str, default: Any = None) -> Any:
        return self.extras.get(key, default)
