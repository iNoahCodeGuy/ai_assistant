"""Shared fixtures and utilities for common questions tests.

This module provides common test fixtures, sample data, and utility functions
used across all common questions test modules.
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pathlib import Path

# Add the module exports explicitly
__all__ = [
    'temp_analytics', 'sample_interactions', 'realistic_analytics', 'mock_analytics', 
    'display_component', 'assert_question_structure', 'assert_role_questions_structure',
    'create_test_interaction'
]

# Import the modules we're testing
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from src.analytics.comprehensive_analytics import ComprehensiveAnalytics, UserInteraction
    from src.ui.components.common_questions import CommonQuestionsDisplay
except ImportError as e:
    # For testing environments where modules might not be available
    print(f"Warning: Import failed - {e}")
    ComprehensiveAnalytics = Mock
    UserInteraction = Mock
    CommonQuestionsDisplay = Mock


@pytest.fixture
def temp_analytics():
    """Create temporary analytics database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    analytics = ComprehensiveAnalytics(db_path=db_path)
    yield analytics
    analytics.close()
    os.unlink(db_path)


@pytest.fixture
def sample_interactions(temp_analytics):
    """Create sample user interactions for testing."""
    interactions = [
        UserInteraction(
            session_id="session_1",
            timestamp=datetime.now() - timedelta(days=1),
            user_role="Software Developer",
            query="How does the RAG engine work?",
            query_type="technical",
            response_time=2.5,
            response_length=500,
            code_snippets_shown=3,
            citations_provided=5,
            success=True,
            follow_up_query=False,
            conversation_turn=1
        ),
        UserInteraction(
            session_id="session_2",
            timestamp=datetime.now() - timedelta(days=2),
            user_role="Software Developer",
            query="How does the RAG engine work?",  # Duplicate for frequency
            query_type="technical",
            response_time=2.1,
            response_length=450,
            code_snippets_shown=2,
            citations_provided=4,
            success=True,
            follow_up_query=False,
            conversation_turn=1
        ),
        UserInteraction(
            session_id="session_3",
            timestamp=datetime.now() - timedelta(days=3),
            user_role="Hiring Manager (technical)",
            query="What's Noah's technical background?",
            query_type="career",
            response_time=1.8,
            response_length=600,
            code_snippets_shown=1,
            citations_provided=2,
            success=True,
            follow_up_query=False,
            conversation_turn=1
        ),
        UserInteraction(
            session_id="session_4",
            timestamp=datetime.now() - timedelta(days=4),
            user_role="Just looking around",
            query="Tell me about Noah",
            query_type="general",
            response_time=1.2,
            response_length=300,
            code_snippets_shown=0,
            citations_provided=0,
            success=True,
            follow_up_query=False,
            conversation_turn=1
        ),
        UserInteraction(
            session_id="session_5",
            timestamp=datetime.now() - timedelta(days=35),  # Old data
            user_role="Software Developer",
            query="Old question",
            query_type="technical",
            response_time=3.0,
            response_length=200,
            code_snippets_shown=0,
            citations_provided=0,
            success=False,
            follow_up_query=False,
            conversation_turn=1
        )
    ]
    
    for interaction in interactions:
        temp_analytics.log_interaction(interaction)
    
    return interactions


@pytest.fixture
def realistic_analytics():
    """Create analytics with realistic data patterns."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    analytics = ComprehensiveAnalytics(db_path=db_path)
    
    # Simulate realistic question patterns
    realistic_questions = [
        ("What's Noah's background?", "Hiring Manager (nontechnical)", "career", 15),
        ("Show me Noah's code", "Hiring Manager (technical)", "technical", 12), 
        ("How does the RAG work?", "Software Developer", "technical", 10),
        ("Tell me about Noah", "Just looking around", "general", 8),
        ("What's his Python experience?", "Hiring Manager (technical)", "career", 6),
        ("MMA fight", "Just looking around", "mma", 5),
        ("Code architecture?", "Software Developer", "technical", 4),
        ("Career achievements?", "Hiring Manager (nontechnical)", "career", 3)
    ]
    
    for i, (question, role, query_type, frequency) in enumerate(realistic_questions):
        for j in range(frequency):
            interaction = UserInteraction(
                session_id=f"realistic_{i}_{j}",
                timestamp=datetime.now() - timedelta(days=j % 30),
                user_role=role,
                query=question,
                query_type=query_type,
                response_time=1.5 + (j % 3 * 0.5),
                response_length=400 + (j % 5 * 100),
                code_snippets_shown=2 if query_type == "technical" else 0,
                citations_provided=3 if query_type == "technical" else 1,
                success=True,
                follow_up_query=j % 4 == 0,
                conversation_turn=1 + (j % 3)
            )
            analytics.log_interaction(interaction)
    
    yield analytics
    analytics.close()
    os.unlink(db_path)


@pytest.fixture
def mock_analytics():
    """Create mock analytics system."""
    mock = Mock(spec=ComprehensiveAnalytics)
    mock.get_most_common_questions.return_value = [
        {
            'question': "How does the RAG engine work?",
            'frequency': 5,
            'success_rate': 0.9,
            'avg_response_time': 2.3,
            'query_type': 'technical',
            'roles': ['Software Developer']
        },
        {
            'question': "What's Noah's background?",
            'frequency': 3,
            'success_rate': 1.0,
            'avg_response_time': 1.8,
            'query_type': 'career',
            'roles': ['Hiring Manager (technical)']
        }
    ]
    
    mock.get_suggested_questions_for_role.return_value = [
        "How does the RAG engine work?",
        "Show me the code architecture",
        "What's the memory system?"
    ]
    
    mock.get_common_questions_by_role.return_value = {
        'Software Developer': [
            {
                'question': "How does the RAG engine work?",
                'frequency': 5,
                'success_rate': 0.9,
                'query_type': 'technical'
            }
        ],
        'Hiring Manager (technical)': [
            {
                'question': "What's Noah's background?",
                'frequency': 3,
                'success_rate': 1.0,
                'query_type': 'career'
            }
        ]
    }
    
    return mock


@pytest.fixture
def display_component(mock_analytics):
    """Create CommonQuestionsDisplay component."""
    return CommonQuestionsDisplay(analytics_system=mock_analytics)


# Utility functions for assertions
def assert_question_structure(question_data):
    """Assert that question data has the expected structure."""
    required_fields = ['question', 'frequency', 'success_rate']
    for field in required_fields:
        assert field in question_data, f"Question data missing required field: {field}"
    
    assert isinstance(question_data['question'], str)
    assert isinstance(question_data['frequency'], int)
    assert isinstance(question_data['success_rate'], float)
    assert 0.0 <= question_data['success_rate'] <= 1.0


def assert_role_questions_structure(role_questions):
    """Assert that role questions have the expected structure."""
    expected_roles = [
        'Software Developer',
        'Hiring Manager (technical)',
        'Hiring Manager (nontechnical)',
        'Just looking around'
    ]
    
    for role in expected_roles:
        assert role in role_questions, f"Missing role: {role}"
        assert isinstance(role_questions[role], list)


def create_test_interaction(
    session_id="test_session",
    user_role="Software Developer",
    query="Test query",
    query_type="technical",
    success=True,
    days_ago=1
):
    """Create a test UserInteraction with default values."""
    return UserInteraction(
        session_id=session_id,
        timestamp=datetime.now() - timedelta(days=days_ago),
        user_role=user_role,
        query=query,
        query_type=query_type,
        response_time=2.0,
        response_length=400,
        code_snippets_shown=2 if query_type == "technical" else 0,
        citations_provided=3 if query_type == "technical" else 1,
        success=success,
        follow_up_query=False,
        conversation_turn=1
    )
