import pytest
from unittest.mock import Mock, MagicMock
from src.agents.role_router import RoleRouter
from src.core.memory import Memory
from src.core.rag_engine import RagEngine

@pytest.fixture
def mock_rag_engine():
    """Mock RAG engine for testing."""
    mock_engine = Mock(spec=RagEngine)
    mock_engine.retrieve.return_value = [
        {"content": "Noah has intermediate Python skills", "metadata": {"source": "career_kb.csv"}}
    ]
    mock_engine.generate_response.return_value = "Noah's Python skills are at intermediate level with experience in data analysis and automation."
    return mock_engine

@pytest.fixture
def mock_memory():
    """Mock Memory for testing."""
    return Mock(spec=Memory)

@pytest.fixture
def role_router():
    """Create RoleRouter instance."""
    return RoleRouter(max_context_tokens=1000)

def test_role_router_initialization(role_router):
    """Test RoleRouter initializes with correct token limit."""
    assert role_router.max_context_tokens == 1000

def test_chat_history_truncation(role_router):
    """Test chat history truncation based on token budget."""
    # Create long chat history
    long_history = []
    for i in range(20):
        long_history.append({"role": "user", "content": f"Very long message number {i} " * 50})
        long_history.append({"role": "assistant", "content": f"Long response {i} " * 50})
    
    truncated = role_router._truncate_chat_history(long_history)
    
    # Should be truncated
    assert len(truncated) < len(long_history)
    assert len(truncated) > 0

def test_context_building_from_history(role_router):
    """Test building context string from chat history."""
    chat_history = [
        {"role": "user", "content": "What's Noah's background?"},
        {"role": "assistant", "content": "Noah has experience in sales and tech."},
        {"role": "user", "content": "Tell me about his Python skills."}
    ]
    
    context = role_router._build_context_from_history(chat_history)
    
    assert "Previous conversation:" in context
    assert "Human: What's Noah's background?" in context
    assert "Assistant: Noah has experience in sales and tech." in context
    assert "Human: Tell me about his Python skills." in context

def test_nontechnical_manager_routing(role_router, mock_memory, mock_rag_engine):
    """Test routing for nontechnical hiring managers."""
    user_input = "What's Noah's experience?"
    chat_history = [{"role": "user", "content": "Hello"}]
    
    response = role_router.route(
        "Hiring Manager (nontechnical)",
        user_input,
        mock_memory,
        mock_rag_engine,
        chat_history
    )
    
    assert response is not None
    mock_rag_engine.retrieve.assert_called_once()
    mock_rag_engine.generate_response.assert_called_once()

def test_technical_manager_routing(role_router, mock_memory, mock_rag_engine):
    """Test routing for technical hiring managers."""
    user_input = "Show me Noah's Python projects"
    chat_history = []
    
    response = role_router.route(
        "Hiring Manager (technical)",
        user_input,
        mock_memory,
        mock_rag_engine,
        chat_history
    )
    
    assert response is not None
    # Should retrieve more documents for technical queries
    mock_rag_engine.retrieve.assert_called_with(user_input, top_k=5)

def test_developer_routing(role_router, mock_memory, mock_rag_engine):
    """Test routing for software developers."""
    user_input = "Explain Noah's code architecture"
    
    response = role_router.route(
        "Software Developer",
        user_input,
        mock_memory,
        mock_rag_engine
    )
    
    assert response is not None
    # Should retrieve most documents for developer queries
    mock_rag_engine.retrieve.assert_called_with(user_input, top_k=7)

def test_casual_visitor_routing(role_router, mock_memory, mock_rag_engine):
    """Test routing for casual visitors."""
    user_input = "Tell me something interesting about Noah"
    
    response = role_router.route(
        "Just looking around",
        user_input,
        mock_memory,
        mock_rag_engine
    )
    
    assert response is not None
    mock_rag_engine.retrieve.assert_called_with(user_input, top_k=3)

def test_confession_routing(role_router, mock_memory, mock_rag_engine):
    """Test routing for confession role."""
    user_input = "I have something to tell Noah"
    
    response = role_router.route(
        "Looking to confess crush",
        user_input,
        mock_memory,
        mock_rag_engine
    )
    
    assert "Thank you for sharing" in response
    assert "LinkedIn" in response
    # Should not call RAG engine for confessions
    mock_rag_engine.retrieve.assert_not_called()

def test_context_preservation_across_turns(role_router, mock_memory, mock_rag_engine):
    """Test that context from previous turns is preserved."""
    # First turn
    chat_history_1 = []
    role_router.route(
        "Software Developer",
        "What languages does Noah use?",
        mock_memory,
        mock_rag_engine,
        chat_history_1
    )
    
    # Second turn with history
    chat_history_2 = [
        {"role": "user", "content": "What languages does Noah use?"},
        {"role": "assistant", "content": "Noah uses Python primarily."}
    ]
    
    # Mock to capture the prompt used
    def capture_prompt(prompt, docs):
        assert "Previous conversation:" in prompt
        assert "What languages does Noah use?" in prompt
        return "Response with context"
    
    mock_rag_engine.generate_response.side_effect = capture_prompt
    
    role_router.route(
        "Software Developer",
        "How advanced is his Python?",
        mock_memory,
        mock_rag_engine,
        chat_history_2
    )