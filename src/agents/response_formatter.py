from typing import Any, Dict, Tuple, List
import re
from typing import Dict, Any, List
from langchain.schema import Document

class ResponseFormatter:
    """Formats responses based on role and content type."""

    def format(self, response_data: Dict[str, Any]) -> str:
        response = response_data.get("response", "")
        rtype = response_data.get("type", "general")
        context = response_data.get("context", [])
        
        # Convert context dict to list if needed
        if isinstance(context, dict):
            # Extract matches from the dict returned by retrieve()
            context = context.get("matches", [])
        elif context is None:
            context = []

        if rtype == "technical":
            return self._format_technical_response(response, context)
        if rtype == "mma":
            return self._format_mma_response(response_data)
        if rtype == "career":
            return self._format_career_response(response, context)
        if rtype == "fun":
            return self._format_fun_response(response)
        if rtype == "confession":
            return "💌 " + response
        return self._format_general_response(response)

    def _format_technical_response(self, response: str, context: List[Document]) -> str:
        """Enhanced technical formatting with code snippets and proper citations."""
        sections = []
        
        # Engineer Detail Section
        sections.append("## 🔧 Engineer Detail")
        sections.append(response)
        
        # Ensure context is a list
        if not isinstance(context, list):
            context = []
        
        # Code Examples Section (if context contains code snippets)
        code_snippets = [doc for doc in context if hasattr(doc, 'metadata') and doc.metadata.get('type') == 'code']
        if code_snippets:
            sections.append("\n## 💻 Code Examples")
            for snippet in code_snippets[:3]:
                metadata = snippet.metadata
                sections.append(f"\n### {metadata.get('name', 'Code Snippet')}")
                sections.append(f"**File:** `{metadata.get('citation', 'unknown')}`")
                sections.append(f"```python\n{snippet.page_content}\n```")
                if metadata.get('github_url'):
                    sections.append(f"[View on GitHub]({metadata['github_url']})")
        
        # Plain-English Summary
        sections.append("\n## 📋 Plain-English Summary")
        sections.append(self._generate_summary(response))
        
        # Citations Section
        if context and isinstance(context, list):
            sections.append("\n## 📚 Citations")
            for i, doc in enumerate(context[:5], 1):
                if hasattr(doc, 'metadata'):
                    source = doc.metadata.get("source") or doc.metadata.get("file_path", "unknown")
                    line = doc.metadata.get("start_line", "")
                    line_info = f":{line}" if line else ""
                    sections.append(f"{i}. `{source}{line_info}`")
                else:
                    sections.append(f"{i}. {str(doc)[:100]}...")
        
        return "\n".join(sections)

    def _generate_summary(self, technical_text: str) -> str:
        """Generate plain-English summary from technical content."""
        # Simple heuristic - take first 2 sentences and simplify
        sentences = technical_text.split('. ')[:2]
        summary = '. '.join(sentences)
        
        # Replace technical terms with simpler alternatives
        replacements = {
            'FAISS': 'a search system',
            'vector store': 'database',
            'embeddings': 'text representations',
            'RAG': 'information retrieval',
            'LangChain': 'AI framework',
            'AST': 'code analysis',
            'API': 'programming interface'
        }
        
        for tech_term, simple_term in replacements.items():
            summary = summary.replace(tech_term, simple_term)
        
        return summary

    def _format_mma_response(self, data: Dict[str, Any]) -> str:
        base = data.get("response", "")
        link = data.get("youtube_link")
        if link:
            return f"{base}\n\nWatch: {link}"
        return base

    def _format_career_response(self, response: str, context: List[Document]) -> str:
        """Format career/technical responses with sources."""
        # Ensure context is a list
        if not isinstance(context, list):
            context = []
        
        # Build better source citations
        if context:
            sources_list = []
            for i, doc in enumerate(context[:3], 1):
                # Handle both Document objects and dicts
                if hasattr(doc, 'metadata'):
                    # Document object - extract from metadata
                    metadata = doc.metadata
                    source = metadata.get('source', 'unknown')
                    doc_id = metadata.get('doc_id', '')
                    section = metadata.get('section', '')[:80] if metadata.get('section') else ''
                    similarity = metadata.get('similarity', 0)
                    if not similarity and hasattr(doc, 'similarity'):
                        similarity = doc.similarity
                elif isinstance(doc, dict):
                    # Dict from pgvector_retriever - fields are at top level
                    source = doc.get('source', 'unknown')
                    doc_id = doc.get('doc_id', '')
                    section = doc.get('section', '')[:80] if doc.get('section') else ''
                    similarity = doc.get('similarity', 0)
                else:
                    continue
                
                # Format source with more detail
                if section and doc_id:
                    sources_list.append(f"{i}. **{doc_id}** - {section} (similarity: {similarity:.2f})")
                elif doc_id:
                    sources_list.append(f"{i}. **{doc_id}** (similarity: {similarity:.2f})")
                else:
                    sources_list.append(f"{i}. **{source}** (similarity: {similarity:.2f})")
            
            sources_text = "\n".join(sources_list) if sources_list else "- (no sources)"
        else:
            sources_text = "- (no sources)"
        
        return f"{response}\n\n---\n\n### 📚 Sources\n{sources_text}"

    def _format_fun_response(self, response: str) -> str:
        return f"### Fun Facts\n{response}"

    def _format_general_response(self, response: str) -> str:
        return response