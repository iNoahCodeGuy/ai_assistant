"""Tests for analytics system question tracking and retrieval.

This module tests the core analytics functionality for tracking
and retrieving common questions from user interactions.
"""

import pytest
import os
import time
from datetime import datetime, timedelta

# Import shared fixtures
try:
    from .common_questions_fixtures import (
        temp_analytics, sample_interactions, realistic_analytics,
        assert_question_structure, assert_role_questions_structure,
        create_test_interaction
    )
except ImportError:
    from common_questions_fixtures import (
        temp_analytics, sample_interactions, realistic_analytics,
        assert_question_structure, assert_role_questions_structure,
        create_test_interaction
    )

# Import modules under test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.analytics.comprehensive_analytics import (
    ComprehensiveAnalytics, UserInteraction, create_interaction_from_rag_result
)


class TestAnalyticsQuestionTracking:
    """Test analytics system question tracking and retrieval."""
    
    def test_get_most_common_questions_all_roles(self, temp_analytics, sample_interactions):
        """Test retrieving most common questions across all roles."""
        questions = temp_analytics.get_most_common_questions(days=30, limit=10)
        
        assert len(questions) >= 1
        
        # Most frequent question should be first
        most_common = questions[0]
        assert_question_structure(most_common)
        assert most_common['question'] == "How does the RAG engine work?"
        assert most_common['frequency'] == 2
        assert most_common['success_rate'] == 1.0
        assert 'Software Developer' in most_common['roles']
    
    def test_get_most_common_questions_by_role(self, temp_analytics, sample_interactions):
        """Test retrieving most common questions filtered by role."""
        dev_questions = temp_analytics.get_most_common_questions(
            role="Software Developer", days=30, limit=5
        )
        
        assert len(dev_questions) >= 1
        assert dev_questions[0]['question'] == "How does the RAG engine work?"
        assert dev_questions[0]['frequency'] == 2
        
        # Test different role
        hm_questions = temp_analytics.get_most_common_questions(
            role="Hiring Manager (technical)", days=30, limit=5
        )
        
        assert len(hm_questions) >= 1
        assert hm_questions[0]['question'] == "What's Noah's technical background?"
        assert hm_questions[0]['frequency'] == 1
    
    def test_get_most_common_questions_time_filtering(self, temp_analytics, sample_interactions):
        """Test that time filtering works correctly."""
        # Recent questions only (7 days)
        recent_questions = temp_analytics.get_most_common_questions(days=7, limit=10)
        
        # Should not include the 35-day-old question
        question_texts = [q['question'] for q in recent_questions]
        assert "Old question" not in question_texts
        
        # All questions (40 days)
        all_questions = temp_analytics.get_most_common_questions(days=40, limit=10)
        all_question_texts = [q['question'] for q in all_questions]
        assert "Old question" in all_question_texts
    
    def test_get_common_questions_by_role_grouped(self, temp_analytics, sample_interactions):
        """Test getting questions grouped by all roles."""
        role_questions = temp_analytics.get_common_questions_by_role(days=30, limit_per_role=3)
        
        assert isinstance(role_questions, dict)
        assert_role_questions_structure(role_questions)
        
        # Check that we got questions for roles with data
        dev_questions = role_questions['Software Developer']
        assert len(dev_questions) >= 1
        assert dev_questions[0]['question'] == "How does the RAG engine work?"
    
    def test_get_suggested_questions_for_role(self, temp_analytics, sample_interactions):
        """Test getting suggested questions based on successful queries."""
        suggestions = temp_analytics.get_suggested_questions_for_role(
            role="Software Developer", limit=3
        )
        
        assert isinstance(suggestions, list)
        assert len(suggestions) >= 1
        assert "How does the RAG engine work?" in suggestions
    
    def test_suggested_questions_success_filtering(self, temp_analytics, sample_interactions):
        """Test that suggested questions only include successful ones."""
        # Add a failed interaction
        failed_interaction = create_test_interaction(
            session_id="fail_session",
            query="Failed query that should not appear",
            success=False
        )
        temp_analytics.log_interaction(failed_interaction)
        
        suggestions = temp_analytics.get_suggested_questions_for_role(
            role="Software Developer", limit=10
        )
        
        # Failed query should not appear in suggestions
        assert "Failed query that should not appear" not in suggestions
    
    def test_empty_database_handling(self, temp_analytics):
        """Test behavior with empty database."""
        # Don't add any sample interactions
        questions = temp_analytics.get_most_common_questions(days=30, limit=10)
        assert questions == []
        
        role_questions = temp_analytics.get_common_questions_by_role()
        for role_list in role_questions.values():
            assert role_list == []
        
        suggestions = temp_analytics.get_suggested_questions_for_role("Software Developer")
        assert suggestions == []


class TestRagIntegration:
    """Test integration with RAG engine results."""
    
    def test_create_interaction_from_rag_result(self):
        """Test creating UserInteraction from RAG engine result."""
        rag_result = {
            'response': 'This is a test response with detailed information.',
            'code_snippets': [
                {'citation': 'src/core/rag_engine.py:100-120'},
                {'citation': 'src/retrieval/code_index.py:50-70'}
            ]
        }
        
        interaction = create_interaction_from_rag_result(
            session_id="test_session",
            user_role="Software Developer",
            query="How does the system work?",
            query_type="technical",
            response_time=2.5,
            rag_result=rag_result
        )
        
        assert interaction.session_id == "test_session"
        assert interaction.user_role == "Software Developer"
        assert interaction.query == "How does the system work?"
        assert interaction.query_type == "technical"
        assert interaction.response_time == 2.5
        assert interaction.response_length == len(rag_result['response'])
        assert interaction.code_snippets_shown == 2
        assert interaction.citations_provided == 2
        assert interaction.success is True
    
    def test_create_interaction_empty_result(self):
        """Test creating UserInteraction from empty RAG result."""
        rag_result = {}
        
        interaction = create_interaction_from_rag_result(
            session_id="test_session",
            user_role="Software Developer", 
            query="Test query",
            query_type="technical",
            response_time=1.0,
            rag_result=rag_result
        )
        
        assert interaction.response_length == 0
        assert interaction.code_snippets_shown == 0
        assert interaction.citations_provided == 0
        assert interaction.success is False


class TestAnalyticsPerformance:
    """Test analytics database performance characteristics."""
    
    def test_analytics_database_performance(self):
        """Test analytics database performance with large datasets."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            analytics = ComprehensiveAnalytics(db_path=db_path)
            
            # Create large number of interactions
            start_time = time.time()
            
            for i in range(100):
                interaction = create_test_interaction(
                    session_id=f"perf_session_{i}",
                    user_role=["Software Developer", "Hiring Manager (technical)"][i % 2],
                    query=f"Performance test query {i}",
                    query_type=["technical", "career"][i % 2],
                    days_ago=i % 30
                )
                analytics.log_interaction(interaction)
            
            insert_time = time.time() - start_time
            
            # Test query performance
            start_time = time.time()
            questions = analytics.get_most_common_questions(days=30, limit=10)
            query_time = time.time() - start_time
            
            # Performance assertions
            assert insert_time < 5.0  # Should insert 100 records in under 5 seconds
            assert query_time < 1.0   # Should query in under 1 second
            assert len(questions) > 0
            
            analytics.close()
            
        finally:
            os.unlink(db_path)
    
    def test_analytics_error_handling(self):
        """Test analytics system error handling."""
        # Test with invalid database path
        with pytest.raises(Exception):
            analytics = ComprehensiveAnalytics(db_path="/invalid/path/database.db")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
