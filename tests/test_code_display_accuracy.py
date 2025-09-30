"""Comprehensive tests for code display and explanation functionality.

Tests the complete pipeline: code indexing → retrieval → formatting → citation accuracy.
Ensures technical roles receive proper code snippets with accurate file:line references.
"""
import pytest
from pathlib import Path
import tempfile
import time
from unittest.mock import patch, MagicMock

from src.core.rag_engine import RagEngine
from src.config.settings import Settings
from src.agents.role_router import RoleRouter
from src.agents.response_formatter import ResponseFormatter
from src.core.memory import Memory
from src.retrieval.code_index import CodeIndex


class TestCodeDisplayAccuracy:
    """Test accurate code display and citation functionality."""
    
    @pytest.fixture
    def rag_engine_with_code(self):
        """Create RagEngine with real code index."""
        settings = Settings()
        settings.disable_auto_rebuild = True  # Deterministic for tests
        return RagEngine(settings=settings)
    
    def test_code_snippets_include_required_fields(self, rag_engine_with_code):
        """Test that code snippets contain all required metadata."""
        result = rag_engine_with_code.retrieve_with_code(
            "RagEngine initialization", 
            role="Software Developer"
        )
        
        assert result.get('has_code') is not None
        assert 'code_snippets' in result
        assert 'code_index_version' in result
        
        if result['code_snippets']:
            snippet = result['code_snippets'][0]
            required_fields = ['file', 'citation', 'content', 'name', 'github_url', 'line_start', 'line_end']
            for field in required_fields:
                assert field in snippet, f"Missing required field: {field}"
    
    def test_citation_format_accuracy(self, rag_engine_with_code):
        """Test that citations follow file:line format."""
        result = rag_engine_with_code.retrieve_with_code(
            "retrieve_with_code", 
            role="Hiring Manager (technical)"
        )
        
        for snippet in result.get('code_snippets', []):
            citation = snippet['citation']
            # Should be format: src/core/rag_engine.py:195-232
            assert ':' in citation, f"Citation missing colon: {citation}"
            
            file_part, line_part = citation.split(':', 1)
            assert file_part.endswith('.py'), f"Citation should reference .py file: {file_part}"
            
            # Line part should contain numbers
            assert any(c.isdigit() for c in line_part), f"Citation should contain line numbers: {line_part}"
    
    def test_github_url_generation(self, rag_engine_with_code):
        """Test that GitHub URLs are properly formatted."""
        result = rag_engine_with_code.retrieve_with_code(
            "code_index", 
            role="Software Developer"
        )
        
        for snippet in result.get('code_snippets', []):
            github_url = snippet['github_url']
            assert github_url.startswith('https://github.com/'), f"Invalid GitHub URL: {github_url}"
            assert '#L' in github_url, f"GitHub URL should contain line anchor: {github_url}"
    
    def test_code_content_not_empty(self, rag_engine_with_code):
        """Test that retrieved code content is meaningful."""
        result = rag_engine_with_code.retrieve_with_code(
            "class RagEngine", 
            role="Software Developer"
        )
        
        for snippet in result.get('code_snippets', []):
            content = snippet['content']
            assert len(content.strip()) > 10, f"Code content too short: {content[:50]}..."
            assert any(keyword in content for keyword in ['def ', 'class ', 'import ', 'return ']), \
                f"Code content doesn't look like Python: {content[:100]}..."


class TestTechnicalResponseGeneration:
    """Test complete technical response generation with code integration."""
    
    @pytest.fixture
    def complete_setup(self):
        """Setup all components for end-to-end testing."""
        settings = Settings()
        rag_engine = RagEngine(settings=settings)
        router = RoleRouter()
        formatter = ResponseFormatter()
        memory = Memory()
        return {
            'rag_engine': rag_engine,
            'router': router, 
            'formatter': formatter,
            'memory': memory
        }
    
    def test_technical_hiring_manager_gets_code(self, complete_setup):
        """Test technical hiring manager receives code snippets and explanations."""
        components = complete_setup
        
        # Test technical query routing
        response = components['router'].route(
            role="Hiring Manager (technical)",
            query="How does Noah's RAG architecture work?",
            memory=components['memory'],
            rag_engine=components['rag_engine'],
            chat_history=[]
        )
        
        assert response is not None
        assert 'response' in response
        
        # Should contain technical details
        response_text = response['response']
        technical_indicators = ['Engineer Detail', 'Code References', 'file:', 'line', 'github.com']
        assert any(indicator in response_text for indicator in technical_indicators), \
            f"Technical response missing code details: {response_text[:200]}..."
    
    def test_software_developer_gets_detailed_code(self, complete_setup):
        """Test software developer receives maximum code detail."""
        components = complete_setup
        
        response = components['router'].route(
            role="Software Developer", 
            query="Explain the retrieve_with_code implementation",
            memory=components['memory'],
            rag_engine=components['rag_engine'],
            chat_history=[]
        )
        
        response_text = response['response']
        
        # Should contain detailed code information
        code_indicators = ['```python', 'def ', 'src/', '.py:', 'implementation']
        found_indicators = [ind for ind in code_indicators if ind in response_text]
        assert len(found_indicators) >= 2, \
            f"Developer response lacks sufficient code detail. Found: {found_indicators}"
    
    def test_nontechnical_manager_no_code_clutter(self, complete_setup):
        """Test nontechnical hiring manager doesn't get overwhelming code details."""
        components = complete_setup
        
        response = components['router'].route(
            role="Hiring Manager (nontechnical)",
            query="What's Noah's technical background?",
            memory=components['memory'], 
            rag_engine=components['rag_engine'],
            chat_history=[]
        )
        
        response_text = response['response']
        
        # Should focus on career/business value, not code implementation
        business_indicators = ['experience', 'background', 'skills', 'projects']
        code_clutter = ['```python', 'def __init__', 'import ', 'src/core/']
        
        business_count = sum(1 for ind in business_indicators if ind.lower() in response_text.lower())
        code_count = sum(1 for ind in code_clutter if ind in response_text)
        
        assert business_count >= code_count, \
            f"Nontechnical response too code-heavy. Business: {business_count}, Code: {code_count}"


class TestCodeIndexRealtime:
    """Test code index updates and real-time accuracy."""
    
    def test_code_index_detects_file_changes(self):
        """Test that code index detects when source files change."""
        settings = Settings()
        settings.disable_auto_rebuild = False
        engine = RagEngine(settings=settings)
        
        initial_version = engine.code_index_version()
        
        # Create a temporary Python file in the source tree
        temp_file = Path('src/utils/test_probe_temp.py')
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with temp_file.open('w') as f:
                f.write(f"""
# Test file for code index detection
def test_function_{int(time.time())}():
    return "test"
""")
            
            time.sleep(0.1)  # Ensure filesystem timestamp difference
            
            # Trigger code index refresh
            engine.retrieve_with_code("test function", role="Software Developer")
            
            new_version = engine.code_index_version()
            assert new_version != initial_version, \
                "Code index version should change when source files are modified"
        
        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
    
    def test_code_search_quality(self):
        """Test that code search returns relevant, high-quality results."""
        settings = Settings()
        code_index = CodeIndex('.')
        
        # Test search for known functionality
        results = code_index.search_code("retrieve_with_code", max_results=3)
        
        assert len(results) > 0, "Should find retrieve_with_code functionality"
        
        # Verify results contain actual relevant code
        found_method = False
        for result in results:
            if 'retrieve_with_code' in result['content']:
                found_method = True
                break
        
        assert found_method, "Search results should contain the actual method implementation"
    
    def test_degraded_mode_fallback(self):
        """Test code display gracefully handles missing code index."""
        # Mock missing code index
        with patch('src.retrieval.code_index.CodeIndex.__init__', side_effect=Exception("Index unavailable")):
            settings = Settings()
            engine = RagEngine(settings=settings)
            
            # Should still work without crashing
            result = engine.retrieve_with_code("test query", role="Software Developer")
            
            assert 'code_snippets' in result
            assert result['has_code'] is False
            assert len(result['code_snippets']) == 0


class TestResponseFormatting:
    """Test formatting of technical responses with code."""
    
    def test_engineer_detail_section_present(self):
        """Test that technical responses include Engineer Detail section."""
        formatter = ResponseFormatter()
        
        # Mock response data with code snippets
        response_data = {
            'type': 'technical',
            'response': 'Technical explanation of the system',
            'context': [
                type('MockDoc', (), {
                    'page_content': 'def retrieve_with_code(self):',
                    'metadata': {
                        'type': 'code',
                        'name': 'retrieve_with_code',
                        'citation': 'src/core/rag_engine.py:195',
                        'github_url': 'https://github.com/test/repo#L195'
                    }
                })()
            ]
        }
        
        formatted = formatter.format(response_data)
        
        # Should contain structured sections
        expected_sections = ['Engineer Detail', 'Code Examples', 'Plain-English Summary']
        found_sections = [section for section in expected_sections if section in formatted]
        
        assert len(found_sections) >= 2, f"Missing technical sections. Found: {found_sections}"
    
    def test_plain_english_summary_generation(self):
        """Test generation of business-friendly summaries."""
        formatter = ResponseFormatter()
        
        technical_text = "The FAISS vector store uses embeddings to perform similarity search across career knowledge base entries using LangChain's retrieval interface."
        
        summary = formatter._generate_summary(technical_text)
        
        # Should replace technical terms
        technical_terms = ['FAISS', 'embeddings', 'vector store', 'LangChain']
        simplified_terms = ['search system', 'text representations', 'database', 'AI framework']
        
        # At least some technical terms should be simplified
        simplified_count = sum(1 for term in simplified_terms if term in summary)
        assert simplified_count > 0, f"Summary should contain simplified terms: {summary}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
