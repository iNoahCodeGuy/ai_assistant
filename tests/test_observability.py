"""Tests for observability module.

Tests cover:
- LangSmith tracer initialization
- Metric calculations
- LLM-based evaluation
- Agentic workflow
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

# Test fixtures
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response for testing."""
    response = Mock()
    response.choices = [Mock(message=Mock(content="Test response"))]
    response.usage = Mock(prompt_tokens=50, completion_tokens=100)
    return response


@pytest.fixture
def sample_chunks():
    """Sample retrieval chunks for testing."""
    return [
        {'content': 'Noah is proficient in Python, JavaScript, and TypeScript.', 'score': 0.85, 'source': 'career_kb'},
        {'content': 'He has experience with React, FastAPI, and LangChain.', 'score': 0.78, 'source': 'career_kb'},
        {'content': 'Noah built a RAG system using pgvector and Supabase.', 'score': 0.72, 'source': 'projects'}
    ]


class TestLangSmithTracer:
    """Test LangSmith integration."""
    
    def test_initialize_langsmith_enabled(self):
        """Test LangSmith initialization when configured."""
        with patch.dict(os.environ, {
            'LANGCHAIN_TRACING_V2': 'true',
            'LANGCHAIN_API_KEY': 'lsv2_pt_test_key'
        }):
            from observability.langsmith_tracer import initialize_langsmith
            result = initialize_langsmith()
            assert result is True
    
    def test_initialize_langsmith_disabled(self):
        """Test LangSmith initialization when not configured."""
        with patch.dict(os.environ, {
            'LANGCHAIN_TRACING_V2': 'false'
        }, clear=True):
            from observability.langsmith_tracer import initialize_langsmith
            result = initialize_langsmith()
            assert result is False
    
    def test_trace_retrieval_decorator(self, sample_chunks):
        """Test retrieval tracing decorator."""
        from observability.langsmith_tracer import trace_retrieval
        
        @trace_retrieval
        def mock_retrieve(query: str, top_k: int = 3):
            return {'matches': sample_chunks, 'scores': [0.85, 0.78, 0.72]}
        
        result = mock_retrieve("What are Noah's skills?")
        assert 'matches' in result
        assert len(result['matches']) == 3
    
    def test_trace_generation_decorator(self, mock_openai_response):
        """Test generation tracing decorator."""
        from observability.langsmith_tracer import trace_generation
        
        @trace_generation
        def mock_generate(prompt: str):
            return mock_openai_response
        
        result = mock_generate("Test prompt")
        assert hasattr(result, 'choices')
        assert result.usage.prompt_tokens == 50


class TestMetrics:
    """Test metrics calculation."""
    
    def test_retrieval_metrics_creation(self, sample_chunks):
        """Test RetrievalMetrics creation."""
        from observability.metrics import calculate_retrieval_metrics
        
        metrics = calculate_retrieval_metrics(
            query="What are Noah's skills?",
            chunks=sample_chunks,
            latency_ms=150
        )
        
        assert metrics.query == "What are Noah's skills?"
        assert metrics.num_chunks == 3
        assert metrics.latency_ms == 150
        assert 0.7 < metrics.avg_similarity < 0.9
        assert len(metrics.similarity_scores) == 3
    
    def test_generation_metrics_creation(self):
        """Test GenerationMetrics creation."""
        from observability.metrics import calculate_generation_metrics
        
        metrics = calculate_generation_metrics(
            prompt="Test prompt",
            response="Test response",
            tokens_prompt=50,
            tokens_completion=100,
            latency_ms=800,
            model="gpt-4"
        )
        
        assert metrics.prompt == "Test prompt"
        assert metrics.response == "Test response"
        assert metrics.tokens_prompt == 50
        assert metrics.tokens_completion == 100
        assert metrics.total_tokens == 150
        assert metrics.latency_ms == 800
        assert metrics.cost_usd > 0
    
    def test_openai_cost_calculation(self):
        """Test cost estimation."""
        from observability.metrics import calculate_openai_cost
        
        # GPT-4 pricing
        cost_gpt4 = calculate_openai_cost("gpt-4", 1000, 1000)
        assert cost_gpt4 == 0.09  # $0.03 + $0.06
        
        # GPT-3.5-turbo pricing
        cost_gpt35 = calculate_openai_cost("gpt-3.5-turbo", 1000, 1000)
        assert cost_gpt35 == 0.0035  # $0.0015 + $0.002


class TestEvaluators:
    """Test LLM-based evaluation functions."""
    
    @patch('observability.evaluators.get_evaluation_client')
    def test_evaluate_faithfulness(self, mock_client, sample_chunks):
        """Test faithfulness evaluation."""
        from observability.evaluators import evaluate_faithfulness
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="SCORE: 0.9\nEXPLANATION: Response is well-grounded in context."))
        ]
        mock_client.return_value.chat.completions.create.return_value = mock_response
        
        context = [c['content'] for c in sample_chunks]
        score, explanation = evaluate_faithfulness(
            query="What are Noah's skills?",
            context=context,
            answer="Noah is proficient in Python, JavaScript, and React."
        )
        
        assert 0.0 <= score <= 1.0
        assert isinstance(explanation, str)
        assert len(explanation) > 0
    
    @patch('observability.evaluators.get_evaluation_client')
    def test_evaluate_relevance(self, mock_client, sample_chunks):
        """Test relevance evaluation."""
        from observability.evaluators import evaluate_relevance
        
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="SCORE: 0.85\nEXPLANATION: Context directly answers the query."))
        ]
        mock_client.return_value.chat.completions.create.return_value = mock_response
        
        context = [c['content'] for c in sample_chunks]
        score, explanation = evaluate_relevance(
            query="What programming languages does Noah know?",
            context=context
        )
        
        assert 0.0 <= score <= 1.0
        assert isinstance(explanation, str)
    
    def test_should_evaluate_sample(self):
        """Test sampling function."""
        from observability.evaluators import should_evaluate_sample
        
        # Test with 100% sampling
        results = [should_evaluate_sample(1.0) for _ in range(10)]
        assert all(results)
        
        # Test with 0% sampling
        results = [should_evaluate_sample(0.0) for _ in range(10)]
        assert not any(results)
        
        # Test with 50% sampling (statistical test)
        results = [should_evaluate_sample(0.5) for _ in range(1000)]
        ratio = sum(results) / len(results)
        assert 0.4 < ratio < 0.6  # Should be around 50%


class TestAgenticWorkflow:
    """Test LangGraph agentic workflow."""
    
    def test_classify_intent_technical(self):
        """Test intent classification for technical queries."""
        from observability.agentic_workflow import classify_intent
        
        state = {
            'query': 'What programming languages does Noah know?',
            'role_mode': 'Software Developer'
        }
        
        result = classify_intent(state)
        assert result['intent'] == 'technical'
    
    def test_classify_intent_career(self):
        """Test intent classification for career queries."""
        from observability.agentic_workflow import classify_intent
        
        state = {
            'query': 'What is Noah\'s work experience?',
            'role_mode': 'Hiring Manager'
        }
        
        result = classify_intent(state)
        assert result['intent'] == 'career'
    
    def test_classify_intent_mma(self):
        """Test intent classification for MMA queries."""
        from observability.agentic_workflow import classify_intent
        
        state = {
            'query': 'What martial arts does Noah practice?',
            'role_mode': 'General'
        }
        
        result = classify_intent(state)
        assert result['intent'] == 'mma'
    
    @patch('observability.agentic_workflow.get_retriever')
    def test_retrieve_node(self, mock_retriever, sample_chunks):
        """Test retrieve node in workflow."""
        from observability.agentic_workflow import retrieve
        
        mock_retriever.return_value.retrieve.return_value = sample_chunks
        
        state = {
            'query': 'What are Noah\'s skills?',
            'intent': 'technical'
        }
        
        result = retrieve(state)
        assert 'retrieved_chunks' in result
        assert 'retrieval_scores' in result
        assert len(result['retrieved_chunks']) > 0
    
    def test_should_retry_logic(self):
        """Test retry decision logic."""
        from observability.agentic_workflow import should_retry
        
        # Should retry if no chunks
        state = {'retrieved_chunks': [], 'retry_count': 0}
        assert should_retry(state) == 'retrieve'
        
        # Should not retry if max retries reached
        state = {'retrieved_chunks': [], 'retry_count': 2}
        assert should_retry(state) == 'end'
        
        # Should not retry if chunks retrieved
        state = {'retrieved_chunks': [{'content': 'test'}], 'retry_count': 0}
        assert should_retry(state) == 'end'


class TestIntegration:
    """Integration tests for full observability pipeline."""
    
    @pytest.mark.skipif(
        os.getenv('LANGCHAIN_TRACING_V2') != 'true',
        reason="LangSmith not configured"
    )
    def test_full_rag_with_observability(self):
        """Test full RAG pipeline with observability enabled."""
        from core.rag_engine import RagEngine
        
        engine = RagEngine()
        response = engine.generate_response("What are Noah's skills?")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Trace should appear in LangSmith dashboard
    
    def test_metrics_logging_to_supabase(self, sample_chunks):
        """Test metrics logging to Supabase."""
        from observability.metrics import log_metrics_to_supabase, calculate_retrieval_metrics
        
        metrics = calculate_retrieval_metrics(
            query="Test query",
            chunks=sample_chunks,
            latency_ms=100
        )
        
        # This should not fail even if Supabase unavailable
        result = log_metrics_to_supabase(
            retrieval_metrics=metrics,
            message_id=None  # No message ID for test
        )
        
        # Should return bool
        assert isinstance(result, bool)


class TestGracefulDegradation:
    """Test that observability fails gracefully when unavailable."""
    
    def test_rag_works_without_langsmith(self):
        """Test RAG engine works without LangSmith."""
        with patch.dict(os.environ, {'LANGCHAIN_TRACING_V2': 'false'}, clear=True):
            from core.rag_engine import RagEngine
            
            engine = RagEngine()
            # Should work even without observability
            assert engine is not None
    
    def test_decorators_are_noops_without_langsmith(self):
        """Test tracing decorators don't break without LangSmith."""
        with patch.dict(os.environ, {'LANGCHAIN_TRACING_V2': 'false'}, clear=True):
            from observability.langsmith_tracer import trace_retrieval
            
            @trace_retrieval
            def test_func():
                return "success"
            
            result = test_func()
            assert result == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
