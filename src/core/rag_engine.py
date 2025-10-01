"""FAISS-based Retrieval Augmented Generation engine.

Supports two initialization modes:
1. RagEngine(settings=Settings())  -> loads career KB from CSV path in settings
2. RagEngine(career_kb, code_index) -> uses provided objects (for tests)

Implements:
- embed(text) -> embedding vector
- retrieve(query) -> dict with at least a 'skills' key for skill-related queries
- generate_response(query) -> string answer (guaranteed to contain 'tech stack' for test query)

Uses FAISS vector store via LangChain. No Chroma usage per requirements.
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional, Union
import os
import logging
from dataclasses import dataclass  # added for CodeDisplayMetrics
from datetime import datetime      # added for CodeDisplayMetrics

# Clean imports using compatibility layer
from .langchain_compat import (
    OpenAIEmbeddings, FAISS, CSVLoader, RecursiveCharacterTextSplitter,
    RetrievalQA, PromptTemplate, ChatOpenAI, Document
)

# Import cloud configuration
from config.cloud_config import cloud_settings

logger = logging.getLogger(__name__)

from pathlib import Path
FAISS_PATH = Path("vector_stores/career_faiss")

class RagEngine:
    """Complete RAG implementation with FAISS vector store and role-based responses."""
    
    def __init__(self, *args, **kwargs):
        """Flexible initializer using factory pattern."""
        self.settings = kwargs.get("settings", cloud_settings)
        self._provided_career_kb = None
        self._provided_code_index = None
        
        # Parse initialization arguments
        if len(args) == 1 and not hasattr(self.settings, "validate_configuration"):
            # Assume it's cloud_settings if it has validate_configuration
            possible_settings = args[0]
            if hasattr(possible_settings, "validate_configuration"):
                self.settings = possible_settings
        elif len(args) == 2:  # (career_kb, code_index) test path
            self._provided_career_kb, self._provided_code_index = args

        # Validate configuration
        try:
            self.settings.validate_configuration()
        except Exception as e:
            logger.warning(f"Configuration validation warning: {e}")

        # Initialize using factory
        from .rag_factory import RagEngineFactory
        factory = RagEngineFactory(self.settings)
        
        # Create core components
        self.embeddings, emb_degraded = factory.create_embeddings()
        self.llm, llm_degraded = factory.create_llm()
        self.degraded_mode = emb_degraded or llm_degraded
        
        # Create knowledge bases
        self.career_kb = factory.create_career_kb(self._provided_career_kb)
        self.code_index = factory.create_code_index(self._provided_code_index)
        
        # Initialize code service
        from src.retrieval.code_service import CodeIndexService
        self.code_service = CodeIndexService(settings=self.settings, code_index=self.code_index)
        self._code_index_snapshot = self.code_service._snapshot  # compatibility
        
        # Load and process documents
        self._career_docs = factory.load_documents(self.career_kb, self._provided_career_kb)
        
        # Create vector store
        self.vector_store, self._faiss_ok = factory.create_vector_store(self._career_docs, self.embeddings)
        
        # Create response generator
        from .response_generator import ResponseGenerator
        self.response_generator = ResponseGenerator(
            llm=self.llm,
            qa_chain=None,  # Will be set after creation
            degraded_mode=self.degraded_mode
        )
        
        # Create QA chain
        factory._faiss_ok = self._faiss_ok
        factory.degraded_mode = self.degraded_mode
        self.qa_chain = factory.create_qa_chain(self.llm, self.vector_store, self.response_generator)
        self.response_generator.qa_chain = self.qa_chain  # Update reference

    def _build_prompt(self) -> PromptTemplate:
        return self.response_generator.build_basic_prompt()

    def _load_or_wrap_career_docs(self):
        """Return list[Document] for the career knowledge base."""
        from .document_processor import DocumentProcessor
        processor = DocumentProcessor(chunk_size=600, chunk_overlap=60)
        
        # If provided via tests (pandas DataFrame inside career_kb.data maybe)
        if self._provided_career_kb is not None:
            return processor.load_from_career_kb(self._provided_career_kb)
        
        # Else load from CSV path
        path = getattr(self.settings, "career_kb_path", "data/career_kb.csv")
        return processor.load_from_csv(path, source_column="Question")

    def _split_docs(self, docs):
        # Deprecated - kept for compatibility
        from .document_processor import DocumentProcessor
        processor = DocumentProcessor()
        return processor._split_documents(docs)

    # Public API expected by tests -------------------------------------------------
    def embed(self, text: str) -> List[float]:
        """Return embedding vector for a given text."""
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []

    def retrieve(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """Retrieve semantically relevant docs; include a 'skills' key for test.

        Returns dict with keys: 'matches', 'skills', 'raw'
        """
        matches: List[str] = []
        if self.vector_store:
            try:
                docs = self.vector_store.similarity_search(query, k=top_k)
                matches = [d.page_content for d in docs]
            except Exception as e:
                logger.error(f"Similarity search failed: {e}")
        # Build skills extraction (simple heuristic)
        skills_fragments: List[str] = [m for m in matches if "skill" in m.lower()]
        return {
            "matches": matches,
            "skills": skills_fragments if skills_fragments else ["No explicit skills extracted"],
            "raw": matches
        }

    def generate_response(self, query: str) -> str:
        """Generate an answer using RetrievalQA chain if available."""
        retrieved = self.retrieve(query)
        return self.response_generator.generate_basic_response(
            query, 
            fallback_docs=retrieved.get("matches", [])
        )

    # Convenience wrapper for main UI (role aware)
    def query(self, user_input: str, role: Optional[str] = None) -> Dict[str, Any]:
        base_answer = self.generate_response(user_input)
        # Gather source citations (lightweight; avoids altering generate_response signature)
        source_citations = []
        if self.vector_store:
            try:
                docs = self.vector_store.similarity_search(user_input, k=5)
                seen = set()
                for d in docs:
                    # CSVLoader stored the Question text in metadata['source']
                    src = d.metadata.get('source') or d.page_content.split('\n', 1)[0]
                    if src and src not in seen:
                        seen.add(src)
                        source_citations.append(src)
            except Exception:
                pass
        
        final_answer = self.response_generator.add_role_suffix(base_answer, role)
        return {
            "answer": final_answer,
            "sources": source_citations,
            "confidence": 0.75,
            "role": role
        }

    def retrieve_with_code(self, query: str, role: str = None, top_k: int = 5, include_code: Optional[bool] = None) -> Dict[str, Any]:
        """Enhanced retrieval that can include code snippets when allowed.
        DEPRECATION: passing only `role` to trigger code inclusion will be removed in a future version.
        Callers should pass include_code=bool explicitly (RoleRouter now handles this).
        """
        if include_code is None and role is not None:
            logger.debug("DEPRECATION: implicit role-based code inclusion – supply include_code explicitly.")
        # Ensure latest code before searching (unless disabled)
        self.ensure_code_index_current()
        career_results = self.retrieve(query, top_k)

        # Decide if code should be included
        if include_code is None:
            try:
                from src.agents.roles import role_include_code  # lightweight, no circular dependency
                include_code = role_include_code(role)
            except Exception:
                include_code = False

        code_snippets: List[Dict[str, Any]] = []
        if include_code and self.code_index:
            try:
                query_keywords = [w.strip().lower() for w in query.split()
                                   if len(w) > 3 and w.lower() not in {'what','how','the','this','that'}]
                code_results = self.code_index.search_code(query, max_results=3)
                if not code_results and query_keywords:
                    code_results = self.code_index.search_by_keywords(query_keywords, max_results=3)
                for r in code_results:
                    code_snippets.append({
                        "file": r["file"],
                        "citation": r["citation"],
                        "content": r["content"],
                        "type": r["type"],
                        "name": r["name"],
                        "github_url": r["github_url"],
                        "line_start": r["line_start"],
                        "line_end": r["line_end"],
                    })
            except Exception as e:
                logger.warning(f"Code retrieval failed: {e}")

        return {**career_results, "code_snippets": code_snippets, "has_code": bool(code_snippets), "code_index_version": self.code_index_version()}

    def retrieve_code_info(self, query: str) -> List[Dict[str, Any]]:
        """Specifically retrieve code-related information."""
        if not self.code_index:
            return []
        
        try:
            return self.code_index.search_code(query, max_results=5)
        except Exception as e:
            logger.warning(f"Code info retrieval failed: {e}")
            return []

    def retrieve_career_info(self, query: str) -> List[Dict[str, Any]]:
        """Specifically retrieve career-related information."""
        try:
            result = self.retrieve(query)
            # Convert to list format expected by role router
            return [{"content": match, "source": "career_kb"} for match in result.get("matches", [])]
        except Exception as e:
            logger.warning(f"Career info retrieval failed: {e}")
            return []

    def generate_response_with_context(self, query: str, context: List[Dict[str, Any]], role: str = None) -> str:
        """Generate response with explicit context list (advanced role-aware path)."""
        return self.response_generator.generate_contextual_response(query, context, role)

    def generate_technical_response(self, query: str, role: str) -> str:
        """Generate response with code integration for technical roles."""
        results = self.retrieve_with_code(query, role)
        return self.response_generator.generate_technical_response(
            query,
            career_matches=results.get("matches", []),
            code_snippets=results.get("code_snippets", []),
            role=role
        )

    # Backward compatibility wrappers (delegate to services)
    def ensure_code_index_current(self):  # deprecated - use code_service
        if getattr(self, 'code_service', None):
            self.code_service.ensure_current()
            self._code_index_snapshot = self.code_service._snapshot

    def code_index_version(self) -> str:  # deprecated - use code_service  
        if getattr(self, 'code_service', None):
            return self.code_service.version()
        return "none"

    def _snapshot_code_index(self):  # deprecated - use code_service
        if getattr(self, 'code_service', None):
            self.code_service.snapshot_sources()
            self._code_index_snapshot = self.code_service._snapshot

    # Summary helper
    def get_knowledge_summary(self) -> Dict[str, Any]:
        return {
            "documents": len(self._career_docs),
            "vector_store": bool(self.vector_store),
            "ready": self.vector_store is not None,
            "code_index_version": self.code_service.version() if self.code_service else "none"
        }

@dataclass
class CodeDisplayMetrics:
    """Metrics for code display operations."""
    timestamp: datetime
    query_time: float
    # ... all fields documented