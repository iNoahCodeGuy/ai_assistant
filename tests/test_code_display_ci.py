"""Integration tests for code display with CI/CD pipeline.

These tests are designed to run in continuous integration environments
and validate the complete code display pipeline end-to-end.
"""
import pytest
import os
import tempfile
import json
from pathlib import Path

from src.core.rag_engine import RagEngine
from src.config.settings import Settings
from src.agents.role_router import RoleRouter
from src.core.memory import Memory


class TestCodeDisplayCI:
    """CI/CD pipeline tests for code display functionality."""
    
    def test_production_like_environment(self):
        """Test code display in a production-like environment setup."""
        # Simulate production environment variables
        test_env = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', 'test-key'),
            'CODE_INDEX_PATH': 'vector_stores/code_index',
            'CAREER_KB_PATH': 'data/career_kb.csv',
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal test environment
            settings = Settings()
            settings.disable_auto_rebuild = True  # Faster for CI
            
            engine = RagEngine(settings=settings)
            router = RoleRouter()
            memory = Memory()
            
            # Test complete user interaction flow
            response = router.route(
                role="Software Developer",
                query="Show me the RagEngine implementation details",
                memory=memory,
                rag_engine=engine,
                chat_history=[]
            )
            
            # Validate response structure
            assert isinstance(response, dict)
            assert 'response' in response
            assert isinstance(response['response'], str)
            assert len(response['response']) > 0
    
    def test_code_display_smoke_test(self):
        """Basic smoke test for all code display components."""
        settings = Settings()
        settings.disable_auto_rebuild = True
        
        # Test component initialization
        engine = RagEngine(settings=settings)
        assert engine is not None
        
        # Test basic retrieval
        result = engine.retrieve_with_code("test", role="Software Developer")
        assert isinstance(result, dict)
        assert 'code_snippets' in result
        assert 'has_code' in result
        
        # Test version tracking
        version = engine.code_index_version()
        assert isinstance(version, str)
    
    def test_api_key_validation(self):
        """Test API key validation for CI environments."""
        settings = Settings()
        
        # Should handle missing API key gracefully
        if not os.getenv('OPENAI_API_KEY'):
            # In CI without API key, should still initialize
            engine = RagEngine(settings=settings)
            assert engine.degraded_mode is True
        else:
            # With API key, should work normally
            engine = RagEngine(settings=settings)
            assert engine is not None
    
    def test_minimal_dependency_mode(self):
        """Test code display with minimal dependencies."""
        # Simulate missing optional dependencies
        with pytest.MonkeyPatch().context() as mp:
            # Mock missing faiss
            mp.setattr('src.core.langchain_compat.FAISS', None)
            
            settings = Settings()
            engine = RagEngine(settings=settings)
            
            # Should still work in degraded mode
            result = engine.retrieve_with_code("test", role="Software Developer")
            assert isinstance(result, dict)
    
    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'), 
        reason="Requires OpenAI API key for live testing"
    )
    def test_live_api_integration(self):
        """Test live API integration when API key is available."""
        settings = Settings()
        engine = RagEngine(settings=settings)
        router = RoleRouter()
        memory = Memory()
        
        # Test actual API call
        response = router.route(
            role="Software Developer",
            query="What is the main purpose of the RagEngine class?",
            memory=memory,
            rag_engine=engine,
            chat_history=[]
        )
        
        # Validate API response
        assert isinstance(response, dict)
        assert 'response' in response
        assert len(response['response']) > 50  # Should be substantial response
        
        # Should contain technical content for developer role
        response_text = response['response'].lower()
        technical_indicators = ['class', 'method', 'implementation', 'code', 'function']
        assert any(indicator in response_text for indicator in technical_indicators)


class TestCodeDisplayHealthChecks:
    """Health check tests for monitoring code display functionality."""
    
    def test_system_health_check(self):
        """Overall system health check for code display."""
        health_status = {
            'rag_engine': False,
            'code_index': False,
            'vector_store': False,
            'response_generation': False
        }
        
        try:
            settings = Settings()
            engine = RagEngine(settings=settings)
            health_status['rag_engine'] = True
            
            # Test code index
            version = engine.code_index_version()
            if version != "none":
                health_status['code_index'] = True
            
            # Test vector store
            if engine.vector_store is not None:
                health_status['vector_store'] = True
            
            # Test response generation
            result = engine.retrieve_with_code("test", role="Software Developer")
            if isinstance(result, dict) and 'code_snippets' in result:
                health_status['response_generation'] = True
                
        except Exception as e:
            pytest.fail(f"Health check failed: {e}")
        
        # Report health status
        print(f"System Health: {health_status}")
        
        # At minimum, basic functionality should work
        assert health_status['rag_engine'] is True
        assert health_status['response_generation'] is True
    
    def test_performance_baseline(self):
        """Establish performance baseline for monitoring."""
        import time
        
        settings = Settings()
        settings.disable_auto_rebuild = True
        engine = RagEngine(settings=settings)
        
        # Measure initialization time
        start_time = time.time()
        test_engine = RagEngine(settings=settings)
        init_time = time.time() - start_time
        
        # Measure query time
        start_time = time.time()
        result = engine.retrieve_with_code("RagEngine", role="Software Developer")
        query_time = time.time() - start_time
        
        # Log performance metrics
        print(f"Performance Baseline:")
        print(f"  Initialization: {init_time:.2f}s")
        print(f"  Query time: {query_time:.2f}s")
        
        # Performance should be reasonable
        assert init_time < 30.0  # Should initialize within 30 seconds
        assert query_time < 10.0  # Queries should complete within 10 seconds
        
        return {
            'init_time': init_time,
            'query_time': query_time,
            'timestamp': time.time()
        }


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
