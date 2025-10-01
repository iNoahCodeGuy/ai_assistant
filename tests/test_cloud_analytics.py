"""Tests for cloud-native analytics system."""

import pytest
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

# Set test environment variables before importing
os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
os.environ['OPENAI_API_KEY'] = 'test-key'

from src.analytics.cloud_analytics import CloudAnalytics, UserInteractionData


class TestCloudAnalytics:
    """Test cloud analytics system."""
    
    @patch('src.analytics.cloud_analytics.create_engine')
    @patch('src.analytics.cloud_analytics.pubsub_v1.PublisherClient')
    def test_analytics_initialization(self, mock_pubsub, mock_engine):
        """Test that CloudAnalytics initializes properly."""
        # Mock the database engine
        mock_engine.return_value = MagicMock()
        mock_pubsub.return_value = MagicMock()
        
        analytics = CloudAnalytics()
        
        assert analytics is not None
        mock_engine.assert_called_once()
    
    def test_user_interaction_data_creation(self):
        """Test creating UserInteractionData objects."""
        interaction = UserInteractionData(
            session_id="test-session",
            timestamp=datetime.utcnow(),
            user_role="Software Developer",
            query="How does the system work?",
            query_type="technical",
            response_time=2.5,
            response_length=150,
            code_snippets_shown=2,
            citations_provided=3,
            success=True,
            conversation_turn=1
        )
        
        assert interaction.session_id == "test-session"
        assert interaction.user_role == "Software Developer"
        assert interaction.query_type == "technical"
        assert interaction.success is True
        assert interaction.response_time == 2.5
    
    @patch('src.analytics.cloud_analytics.create_engine')
    @patch('src.analytics.cloud_analytics.pubsub_v1.PublisherClient')
    def test_health_check_structure(self, mock_pubsub, mock_engine):
        """Test that health check returns proper structure."""
        # Mock the database components
        mock_session = MagicMock()
        mock_session.execute.return_value.scalar.return_value = 1
        mock_session.query.return_value.count.return_value = 100
        mock_session.query.return_value.filter.return_value.count.return_value = 10
        
        analytics = CloudAnalytics()
        analytics.get_db_session = MagicMock(return_value=mock_session)
        
        health = analytics.health_check()
        
        assert 'status' in health
        assert 'database_connected' in health
        assert 'total_interactions' in health
        assert 'recent_interactions_24h' in health
        assert 'pubsub_enabled' in health
        assert 'timestamp' in health


if __name__ == '__main__':
    pytest.main([__file__, '-v'])