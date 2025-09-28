from typing import List, Dict, Any, Optional
import re
from datetime import datetime

class CitationManager:
    """Manages citations and references for AI responses"""
    
    def __init__(self):
        self.citation_styles = {
            "technical": "file:line format with GitHub links",
            "academic": "Author (Year) format", 
            "simple": "Source: filename format"
        }
    
    def generate_citations(self, content: str, search_results: List[Dict[str, Any]], style: str = "technical") -> List[str]:
        """Generate citations based on search results and style"""
        
        citations = []
        
        for result in search_results:
            metadata = result["metadata"]
            
            if style == "technical":
                citation = self._generate_technical_citation(metadata)
            elif style == "academic":
                citation = self._generate_academic_citation(metadata)
            else:  # simple
                citation = self._generate_simple_citation(metadata)
            
            if citation and citation not in citations:
                citations.append(citation)
        
        return citations
    
    def _generate_technical_citation(self, metadata: Dict[str, Any]) -> str:
        """Generate technical citation with file:line format"""
        
        filename = metadata.get("file", "unknown.txt")
        line = metadata.get("line", 1)
        doc_type = metadata.get("type", "document")
        
        # Create GitHub-style citation
        github_base = "https://github.com/iNoahCodeGuy/NoahsAIAssistant-/blob/main"
        
        if doc_type == "resume":
            return f"📄 {filename}:{line} - Resume section"
        elif doc_type == "code":
            return f"💻 [{filename}:{line}]({github_base}/{filename}#L{line}) - Code repository"
        elif doc_type == "fun_facts":
            return f"🎯 {filename}:{line} - Fun facts database"
        else:
            return f"📑 {filename}:{line} - Documentation"
    
    def _generate_academic_citation(self, metadata: Dict[str, Any]) -> str:
        """Generate academic-style citation"""
        
        filename = metadata.get("file", "unknown.txt")
        current_year = datetime.now().year
        
        # Extract author from filename or use Noah as default
        author = "Noah" if "noah" in filename.lower() else "Documentation"
        
        return f"{author} ({current_year}). {filename}"
    
    def _generate_simple_citation(self, metadata: Dict[str, Any]) -> str:
        """Generate simple citation format"""
        
        filename = metadata.get("file", "unknown.txt") 
        section = metadata.get("section", "")
        
        if section:
            return f"Source: {filename} - {section}"
        else:
            return f"Source: {filename}"
    
    def extract_code_references(self, content: str) -> List[str]:
        """Extract code references from content"""
        
        # Pattern to match file:line references
        pattern = r'([a-zA-Z0-9_\-\.]+\.(py|js|ts|java|cpp|c|h|md|txt)):\s*(\d+)'
        matches = re.findall(pattern, content)
        
        references = []
        for match in matches:
            filename = match[0]
            line_num = match[2]
            references.append(f"{filename}:{line_num}")
        
        return references
    
    def validate_citations(self, citations: List[str]) -> List[str]:
        """Validate and clean citations"""
        
        validated_citations = []
        
        for citation in citations:
            # Remove duplicates and empty citations
            if citation and citation.strip() and citation not in validated_citations:
                validated_citations.append(citation.strip())
        
        return validated_citations
    
    def format_citations_for_display(self, citations: List[str], format_type: str = "markdown") -> str:
        """Format citations for display in UI"""
        
        if not citations:
            return ""
        
        if format_type == "markdown":
            formatted = "\n".join([f"- {citation}" for citation in citations])
        elif format_type == "html":
            formatted = "<ul>\n" + "\n".join([f"<li>{citation}</li>" for citation in citations]) + "\n</ul>"
        else:  # plain text
            formatted = "\n".join([f"• {citation}" for citation in citations])
        
        return formatted
    
    def add_citations_to_response(self, response: str, citations: List[str]) -> str:
        """Add citations to the end of a response"""
        
        if not citations:
            return response
        
        citation_text = "\n\n**Sources:**\n" + self.format_citations_for_display(citations)
        return response + citation_text
    
    def get_citation_stats(self, citations: List[str]) -> Dict[str, Any]:
        """Get statistics about citations"""
        
        stats = {
            "total_citations": len(citations),
            "citation_types": {},
            "file_types": {},
            "has_github_links": 0
        }
        
        for citation in citations:
            # Count citation types
            if "Resume section" in citation:
                stats["citation_types"]["resume"] = stats["citation_types"].get("resume", 0) + 1
            elif "Code repository" in citation:
                stats["citation_types"]["code"] = stats["citation_types"].get("code", 0) + 1
            elif "Fun facts" in citation:
                stats["citation_types"]["fun_facts"] = stats["citation_types"].get("fun_facts", 0) + 1
            else:
                stats["citation_types"]["documentation"] = stats["citation_types"].get("documentation", 0) + 1
            
            # Count file types
            for ext in [".py", ".js", ".md", ".txt", ".pdf"]:
                if ext in citation:
                    stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
            
            # Count GitHub links
            if "github.com" in citation:
                stats["has_github_links"] += 1
        
        return stats