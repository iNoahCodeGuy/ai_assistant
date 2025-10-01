"""Data models and structures for analytics management."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class SessionAnalytics:
    """Session-level analytics tracking."""
    session_id: str
    user_role: str
    start_time: datetime
    last_activity: datetime
    total_queries: int = 0
    successful_queries: int = 0
    avg_response_time: float = 0.0
    total_code_snippets: int = 0
    total_citations: int = 0
    session_rating: Optional[float] = None
    conversion_achieved: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data['start_time'] = self.start_time.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        return data


@dataclass
class DataRetentionPolicy:
    """Data retention configuration."""
    table_name: str
    retention_days: int
    archive_after_days: int
    cleanup_enabled: bool = True
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
