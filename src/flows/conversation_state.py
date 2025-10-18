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

    # Resume distribution tracking (NEW - Intelligent Resume Distribution System)
    hiring_signals: List[str] = field(default_factory=list)  # Passive signal tracking (e.g., "mentioned_hiring", "described_role")
    resume_explicitly_requested: bool = False  # Mode 3 trigger - user asked directly
    resume_sent: bool = False  # Once-per-session enforcement
    user_email: str = ""  # Collected after explicit request
    user_name: str = ""  # For personalization in email
    job_details: Dict[str, str] = field(default_factory=dict)  # {company, position, timeline, team_size} - gathered naturally post-interest

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

    # Resume distribution helper methods
    def add_hiring_signal(self, signal: str) -> None:
        """Add a hiring signal (passive tracking for Mode 2 subtle mentions)."""
        if signal not in self.hiring_signals:
            self.hiring_signals.append(signal)

    def has_hiring_signals(self, min_count: int = 2) -> bool:
        """Check if enough hiring signals detected to enable subtle availability mention."""
        return len(self.hiring_signals) >= min_count

    def mark_resume_requested(self) -> None:
        """Mark that user explicitly requested resume (triggers Mode 3)."""
        self.resume_explicitly_requested = True

    def mark_resume_sent(self) -> None:
        """Mark that resume has been sent (once-per-session enforcement)."""
        self.resume_sent = True

    def set_user_contact(self, email: str, name: str = "") -> None:
        """Store user contact information for resume distribution."""
        self.user_email = email.strip()
        self.user_name = name.strip()

    def add_job_detail(self, key: str, value: str) -> None:
        """Store job details gathered naturally during conversation."""
        self.job_details[key] = value
