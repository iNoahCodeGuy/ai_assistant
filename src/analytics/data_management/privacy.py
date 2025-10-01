"""Privacy management and data anonymization."""

import hashlib
import re
from typing import Any

from ..comprehensive_analytics import UserInteraction


class PrivacyManager:
    """Handle data privacy and anonymization."""
    
    def __init__(self, salt: str = "noah_ai_assistant_2025"):
        """Initialize with configurable salt for hashing."""
        self.salt = salt  # Use environment variable in production
        
        # Patterns for detecting PII
        self.sensitive_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),  # SSN pattern
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),  # Email
            (r'\b\d{3}-\d{3}-\d{4}\b', '[PHONE_REDACTED]'),  # Phone
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD_REDACTED]'),  # Credit card
            (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_REDACTED]'),  # IP address
        ]
    
    def hash_identifier(self, identifier: str) -> str:
        """Create anonymized hash of identifier."""
        if not identifier:
            return ""
        return hashlib.sha256(f"{identifier}{self.salt}".encode()).hexdigest()[:16]
    
    def anonymize_text(self, text: str) -> str:
        """Remove potential PII from text."""
        if not text:
            return text
            
        anonymized = text
        for pattern, replacement in self.sensitive_patterns:
            anonymized = re.sub(pattern, replacement, anonymized)
        
        return anonymized
    
    def anonymize_query(self, query: str) -> str:
        """Remove potential PII from query text."""
        return self.anonymize_text(query)
    
    def anonymize_interaction(self, interaction: UserInteraction) -> UserInteraction:
        """Anonymize user interaction data."""
        return UserInteraction(
            session_id=self.hash_identifier(interaction.session_id),
            timestamp=interaction.timestamp,
            user_role=interaction.user_role,
            query=self.anonymize_query(interaction.query),
            query_type=interaction.query_type,
            response_time=interaction.response_time,
            response_length=interaction.response_length,
            code_snippets_shown=interaction.code_snippets_shown,
            citations_provided=interaction.citations_provided,
            success=interaction.success,
            user_rating=interaction.user_rating,
            follow_up_query=interaction.follow_up_query,
            conversation_turn=interaction.conversation_turn
        )
    
    def check_pii_presence(self, text: str) -> bool:
        """Check if text contains potential PII."""
        if not text:
            return False
            
        for pattern, _ in self.sensitive_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def get_pii_summary(self, text: str) -> dict:
        """Get summary of PII types found in text."""
        summary = {}
        pattern_names = ['SSN', 'Email', 'Phone', 'Credit Card', 'IP Address']
        
        for i, (pattern, _) in enumerate(self.sensitive_patterns):
            matches = re.findall(pattern, text)
            if matches:
                summary[pattern_names[i]] = len(matches)
                
        return summary
