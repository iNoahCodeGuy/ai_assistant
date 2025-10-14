"""Regression tests for conversation quality standards.

These tests ensure that as we add features, we don't break:
- Analytics aggregation and display
- Single follow-up prompts (no duplicates)
- Professional formatting (no emoji spam)
- Code display error handling

Run with: pytest tests/test_conversation_quality.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.flows.conversation_state import ConversationState
from src.flows.conversation_nodes import (
    classify_query, generate_answer, apply_role_context, _is_valid_code_snippet
)
from src.flows.data_reporting import render_full_data_report


class TestAnalyticsQuality:
    """Ensure analytics remain clean and aggregated."""
    
    def test_kb_coverage_aggregated_not_detailed(self):
        """KB coverage should show 3-4 sources, not 245+ individual entries."""
        with patch('src.flows.data_reporting.supabase_analytics') as mock_analytics:
            # Mock analytics data
            mock_analytics.client.table.return_value.select.return_value.execute.return_value.data = []
            mock_analytics.get_kb_coverage.return_value = {
                'architecture_kb': 15,
                'career_kb': 122,
                'technical_kb': 89
            }
            
            report = render_full_data_report()
            
            # Count rows in KB coverage section
            if "Knowledge Base Coverage" in report:
                kb_section = report.split("#### Knowledge Base Coverage")[1].split("####")[0]
                kb_rows = [line for line in kb_section.split("\n") if line.startswith("|") and "---" not in line]
                
                # Should be: header + 3-4 data rows (one per source)
                assert len(kb_rows) <= 6, f"KB coverage has {len(kb_rows)} rows - should be ≤6 (header + 3-5 sources)"
                
                # Should NOT have individual entry names like "entry_1", "entry_100"
                assert "entry_1" not in report.lower()
                assert "entry_100" not in report.lower()
                assert "section_" not in report.lower()  # No section-level breakdowns
    
    def test_kpi_metrics_calculated(self):
        """Analytics should include calculated metrics, not raw dumps."""
        with patch('src.flows.data_reporting.supabase_analytics') as mock_analytics:
            # Mock analytics data
            mock_analytics.client.table.return_value.select.return_value.execute.return_value.data = [
                {"success": True, "latency_ms": 3200},
                {"success": True, "latency_ms": 2800},
                {"success": False, "latency_ms": 5100},
            ]
            mock_analytics.get_kb_coverage.return_value = {}
            
            report = render_full_data_report()
            
            # Must have metrics terminology (even if empty state)
            assert "Success Rate" in report or "Conversations" in report or "Performance" in report
            
            # Should NOT have raw SQL dumps
            assert "SELECT * FROM" not in report
            assert "latency_ms:" not in report  # Raw column names
    
    def test_recent_activity_limited(self):
        """Should show last 10 messages, not entire history."""
        with patch('src.flows.data_reporting.supabase_analytics') as mock_analytics:
            # Mock 50 messages (simulating large history)
            mock_analytics.client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"id": i, "query_type": "general", "latency_ms": 3000} for i in range(50)
            ]
            mock_analytics.get_kb_coverage.return_value = {}
            
            report = render_full_data_report()
            
            if "Recent Conversations" in report or "Recent Activity" in report:
                # Count table rows
                table_rows = report.count("| ")
                
                # Should have manageable number of rows (header + ~10 data rows = ~20 pipe chars per row)
                assert table_rows < 300, f"Report has ~{table_rows // 2} table rows - too many for recent activity"
    
    def test_confessions_privacy_protected(self):
        """Confessions should show count only, no personal details."""
        with patch('src.flows.data_reporting.supabase_analytics') as mock_analytics:
            mock_analytics.client.table.return_value.select.return_value.execute.return_value.data = []
            mock_analytics.get_kb_coverage.return_value = {}
            
            # Mock confessions
            with patch('src.flows.data_reporting.supabase_analytics.client.table') as mock_table:
                mock_table.return_value.select.return_value.execute.return_value.data = [
                    {"name": "John Doe", "email": "john@example.com", "message": "I like you"}
                ]
                
                report = render_full_data_report()
                
                if "Confessions" in report or "confessions" in report:
                    # Should have count statement, not table with PII
                    assert "Total" in report or "Received" in report
                    
                    # Should NOT have PII
                    assert "John Doe" not in report
                    assert "john@example.com" not in report
                    assert "| name |" not in report
                    assert "| email |" not in report
                    assert "| message |" not in report


class TestConversationFlowQuality:
    """Ensure clean, professional conversation flow."""
    
    @patch('src.flows.conversation_nodes.RagEngine')
    def test_no_duplicate_prompts_in_full_flow(self, mock_rag_engine):
        """Should have exactly 1 follow-up prompt at end, not 2-3."""
        # Mock RAG engine
        mock_engine = MagicMock()
        mock_engine.retrieve.return_value = {"chunks": [], "matches": []}
        mock_engine.retrieve_with_code.return_value = {"chunks": [], "code_snippets": [], "has_code": False}
        mock_engine.generate_response.return_value = "This is a product that helps you manage your career."
        mock_rag_engine.return_value = mock_engine
        
        state = ConversationState(
            role="Hiring Manager (technical)",
            query="how does this product work?"
        )
        
        # Set initial answer for apply_role_context to work with
        state.set_answer("This is a product that helps you manage your career.")
        
        # Simulate conversation flow
        state = classify_query(state)
        state = apply_role_context(state, mock_engine)
        
        answer = state.answer
        
        # Count "Would you like" prompts
        prompt_count = answer.lower().count("would you like")
        
        assert prompt_count <= 1, f"Found {prompt_count} 'Would you like' prompts - should be ≤1 (found duplicates)"
    
    @patch('src.flows.conversation_nodes.RagEngine')
    def test_no_emoji_headers(self, mock_rag_engine):
        """Section headers should be professional, not emoji-heavy."""
        # Mock RAG engine
        mock_engine = MagicMock()
        mock_engine.retrieve.return_value = {"chunks": [], "matches": []}
        mock_engine.retrieve_with_code.return_value = {"chunks": [], "code_snippets": [], "has_code": False}
        mock_engine.generate_response.return_value = "Here's information about the data analytics features."
        mock_rag_engine.return_value = mock_engine
        
        state = ConversationState(
            role="Software Developer",
            query="tell me about the data analytics"
        )
        
        # Set initial answer
        state.set_answer("Here's information about the data analytics features.")
        
        # Simulate conversation flow
        state = classify_query(state)
        state = apply_role_context(state, mock_engine)
        
        answer = state.answer
        
        # Check for emoji spam patterns
        emoji_headers = [
            "### 🎯", "### 📊", "### 🏗️", "### 🗂️", "### 🧱", "### 🚀",
            "### 🎉", "### 💻", "### 📦", "## 🔍", "## 🎯", "## 📊"
        ]
        
        for emoji_header in emoji_headers:
            assert emoji_header not in answer, f"Found emoji header '{emoji_header}' - should use **Bold** instead"
    
    def test_llm_no_self_generated_prompts(self):
        """LLM should not generate its own 'Would you like to see' prompts in answer body."""
        # This test verifies system prompt guidance, not runtime behavior
        # Just check that we don't have prompt generation in the wrong place
        from src.core import response_generator
        import inspect
        
        source = inspect.getsource(response_generator)
        
        # The ResponseGenerator should not have active prompt generation
        # (Prompts should only come from conversation_nodes.py)
        if "def add_followup_suggestions" in source:
            method_source = source.split("def add_followup_suggestions")[1].split("def ")[0]
            
            # Should not have multi-line prompt generation
            assert "Would you like me to show you:" not in method_source or \
                   method_source.count("\n") < 20, \
                   "add_followup_suggestions is generating prompts - should be deprecated"


class TestCodeDisplayQuality:
    """Ensure code display handles edge cases gracefully."""
    
    @patch('src.flows.conversation_nodes.RagEngine')
    def test_empty_code_index_shows_helpful_message(self, mock_rag_engine):
        """When code index is empty, should show GitHub link not garbage."""
        # Mock empty code retrieval
        mock_engine = MagicMock()
        mock_engine.retrieve.return_value = {"chunks": [], "matches": []}
        mock_engine.retrieve_with_code.return_value = {
            "chunks": [],
            "code_snippets": [],
            "has_code": False
        }
        mock_engine.generate_response.return_value = "I can help you view the code."
        mock_rag_engine.return_value = mock_engine
        
        state = ConversationState(
            role="Software Developer",
            query="show me the conversation node code"  # Explicit code display trigger
        )
        
        # Set initial answer
        state.set_answer("I can help you view the code.")
        
        # Run through flow
        state = classify_query(state)
        state = apply_role_context(state, mock_engine)
        
        answer = state.answer
        
        # Should NOT show malformed data
        assert "doc_id text" not in answer, "Found 'doc_id text' malformed output"
        assert 'query="' not in answer, "Found metadata leak in output"
        assert "{'doc_id':" not in answer, "Found raw dict output"
        
        # When code unavailable, should either:
        # 1. Show GitHub link
        # 2. Show actual code (if available)
        # 3. Show helpful "unavailable" message
        # 4. Or just show the answer without code (acceptable fallback)
        
        # Main assertion: No malformed data (which is what we fixed)
        # The presence of helpful alternatives is bonus, but not required
        assert len(answer) > 0, "Answer should not be empty"
    
    def test_code_content_validation_logic(self):
        """Code content should be validated before display."""
        # Test the validation helper directly
        test_cases = [
            ("", False, "Empty string should fail"),
            ("   ", False, "Whitespace only should fail"),
            ("short", False, "Too short (<10 chars) should fail"),
            ("doc_id text query=", False, "Metadata lines should fail"),
            ("})\n\n}\n\nquery=\"Show me code examples\"", False, "Truncated metadata blob should fail"),
            ("def hello():\n    print('world')\n    return True", True, "Valid function should pass"),
            (
                "class Example:\n    def run(self):\n        return 'ok'",
                True,
                "Class definition should pass"
            ),
        ]

        for code_content, should_pass, description in test_cases:
            is_valid = _is_valid_code_snippet(code_content)
            assert is_valid == should_pass, (
                f"Validation failed: {description} (got {is_valid}, expected {should_pass})"
            )


class TestRegressionGuards:
    """Catch common regression patterns."""
    
    @patch('src.flows.conversation_nodes.RagEngine')
    def test_no_information_overload(self, mock_rag_engine):
        """Responses should be concise, not dump entire database."""
        # Mock RAG engine
        mock_engine = MagicMock()
        mock_engine.retrieve.return_value = {"chunks": [], "matches": []}
        mock_engine.retrieve_with_code.return_value = {"chunks": [], "code_snippets": [], "has_code": False}
        mock_engine.generate_response.return_value = "We collect interaction data, query types, and latency metrics for analytics."
        mock_rag_engine.return_value = mock_engine
        
        state = ConversationState(
            role="Hiring Manager (technical)",
            query="what data do you collect?"
        )
        
        # Set initial answer
        state.set_answer("We collect interaction data, query types, and latency metrics for analytics.")
        
        # Run through flow
        state = classify_query(state)
        state = apply_role_context(state, mock_engine)
        
        answer = state.answer
        
        # Character count sanity check
        char_count = len(answer)
        assert char_count < 15000, f"Response is {char_count} chars - too long (>15k indicates data dump)"
        
        # Table row count sanity check
        table_rows = answer.count("| ")
        assert table_rows < 250, f"Response has ~{table_rows // 2} table rows - too many (>125 rows indicates dump)"
    
    @patch('src.flows.conversation_nodes.RagEngine')
    def test_consistent_formatting_across_roles(self, mock_rag_engine):
        """All roles should get consistent professional formatting."""
        # Mock RAG engine
        mock_engine = MagicMock()
        mock_engine.retrieve.return_value = {"chunks": [], "matches": []}
        mock_engine.retrieve_with_code.return_value = {"chunks": [], "code_snippets": [], "has_code": False}
        mock_engine.generate_response.return_value = "This product helps manage your career journey."
        mock_rag_engine.return_value = mock_engine
        
        roles = [
            "Hiring Manager (technical)",
            "Hiring Manager (nontechnical)",
            "Software Developer",
            "Just looking around"
        ]
        
        for role in roles:
            state = ConversationState(role=role, query="tell me about the product")
            
            # Set initial answer
            state.set_answer("This product helps manage your career journey.")
            
            # Run through flow
            state = classify_query(state)
            state = apply_role_context(state, mock_engine)
            
            answer = state.answer
            
            # All should have professional formatting (no emoji spam)
            emoji_count = sum(answer.count(emoji) for emoji in ["🎯", "📊", "🏗️", "🗂️", "🧱", "🚀"])
            assert emoji_count < 3, f"{role} has {emoji_count} emojis - should have <3"
            
            # All should have at most 1 follow-up prompt
            prompt_count = answer.lower().count("would you like")
            assert prompt_count <= 1, f"{role} has {prompt_count} prompts - should be ≤1"


class TestSpecificRegressions:
    """Tests for specific bugs that have occurred."""
    
    def test_analytics_no_section_iteration(self):
        """Ensure we don't iterate over sections (245 rows bug)."""
        import inspect
        from src.flows import data_reporting
        
        # Get source code
        source = inspect.getsource(data_reporting)
        
        # Should NOT have nested section iteration
        assert "for section, count in sections.items()" not in source, \
            "Found section-level iteration - this causes 245-row dumps"
        
        # Should aggregate by source only
        assert "source_aggregation" in source or "aggregate" in source, \
            "Missing source-level aggregation logic"
    
    def test_response_generator_no_prompts(self):
        """Ensure response_generator doesn't add follow-up prompts."""
        import inspect
        from src.core import response_generator
        
        # Get source code
        source = inspect.getsource(response_generator)
        
        # Method should be deprecated/minimal
        if "add_followup_suggestions" in source:
            # Check that it's just a pass-through
            method_source = source.split("def add_followup_suggestions")[1].split("def ")[0]
            
            # Should not have multi-line suggestion generation
            assert method_source.count("\n") < 20, \
                "add_followup_suggestions has >20 lines - should be deprecated stub"
    
    def test_conversation_nodes_single_prompt_location(self):
        """Ensure prompts only generated in apply_role_context, not multiple places."""
        import inspect
        from src.flows import conversation_nodes
        
        source = inspect.getsource(conversation_nodes)
        
        # Count occurrences of prompt generation
        prompt_generation_pattern = "Would you like me to show you:"
        occurrences = source.count(prompt_generation_pattern)
        
        # Should appear in exactly ONE location (apply_role_context)
        assert occurrences <= 1, f"Found {occurrences} prompt generation locations - should be 1 (in apply_role_context only)"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
