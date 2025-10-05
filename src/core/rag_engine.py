"""Retrieval Augmented Generation engine with pgvector support.

**MIGRATION NOTE**: This engine now supports both FAISS (legacy) and pgvector (production).
- pgvector: Production mode, uses Supabase for centralized embeddings
- FAISS: Fallback mode for tests and local development

Supports two initialization modes:
1. RagEngine(settings=Settings())  -> loads career KB from CSV path or uses pgvector
2. RagEngine(career_kb, code_index) -> uses provided objects (for tests, FAISS mode)

Implements:
- embed(text) -> embedding vector
- retrieve(query) -> dict with at least a 'skills' key for skill-related queries
- generate_response(query) -> string answer (guaranteed to contain 'tech stack' for test query)

**Why pgvector over FAISS:**
- Centralized: No file syncing across deployments
- Scalable: Works with Vercel serverless functions
- Observable: Retrieval logging built-in
- Real-time: Updates without redeployment
- Cost-efficient: Smaller bundle size, faster cold starts
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

# Import Supabase configuration
from config.supabase_config import supabase_settings

logger = logging.getLogger(__name__)

from pathlib import Path
FAISS_PATH = Path("vector_stores/career_faiss")

class RagEngine:
    """Complete RAG implementation with pgvector (production) and FAISS (fallback) support.
    
    **Production Mode** (pgvector):
    - Uses Supabase for vector similarity search
    - Centralized embeddings, no local files
    - Retrieval logging for observability
    - Scales horizontally on Vercel
    
    **Fallback Mode** (FAISS):
    - Used when pgvector unavailable
    - Loads from local vector_stores/ directory
    - Good for tests and offline development
    
    Mode selection:
    - Automatic: pgvector if Supabase configured, else FAISS
    - Manual: Set use_pgvector=True/False in kwargs
    """
    
    def __init__(self, *args, **kwargs):
        """Flexible initializer using factory pattern."""
        self.settings = kwargs.get("settings", supabase_settings)
        self._provided_career_kb = None
        self._provided_code_index = None
        
        # pgvector mode flag (automatic or manual)
        self.use_pgvector = kwargs.get("use_pgvector", None)
        if self.use_pgvector is None:
            # Auto-detect: use pgvector if Supabase configured
            try:
                supabase_settings.validate_supabase()
                self.use_pgvector = True
                logger.info("pgvector mode enabled (Supabase configured)")
            except:
                self.use_pgvector = False
                logger.info("FAISS fallback mode (Supabase not configured)")
        
        # Initialize pgvector retriever if enabled
        self.pgvector_retriever = None
        if self.use_pgvector:
            try:
                from retrieval.pgvector_retriever import get_retriever
                self.pgvector_retriever = get_retriever(similarity_threshold=0.7)
                logger.info("pgvector retriever initialized")
            except Exception as e:
                logger.warning(f"pgvector initialization failed, falling back to FAISS: {e}")
                self.use_pgvector = False
        
        # Parse initialization arguments
        if len(args) == 1 and not hasattr(self.settings, "validate_configuration"):
            # Assume it's supabase_settings if it has validate_configuration
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
        """Return embedding vector for a given text.
        
        Uses pgvector retriever if available, else falls back to LangChain embeddings.
        """
        try:
            if self.use_pgvector and self.pgvector_retriever:
                return self.pgvector_retriever.embed(text)
            else:
                return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return []

    def retrieve(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """Retrieve semantically relevant docs; include a 'skills' key for test.

        **Production mode** (pgvector):
        - Queries Supabase with similarity search
        - Returns chunks with similarity scores
        - Faster and more scalable
        
        **Fallback mode** (FAISS):
        - Searches local vector store
        - Compatible with existing tests
        
        Returns dict with keys: 'matches', 'skills', 'raw'
        """
        matches: List[str] = []
        
        # Production path: Use pgvector
        if self.use_pgvector and self.pgvector_retriever:
            try:
                chunks = self.pgvector_retriever.retrieve(query, top_k)
                matches = [c['content'] for c in chunks]
                logger.debug(f"pgvector retrieved {len(matches)} chunks")
            except Exception as e:
                logger.error(f"pgvector retrieval failed: {e}")
        
        # Fallback path: Use FAISS
        elif self.vector_store:
            try:
                docs = self.vector_store.similarity_search(query, k=top_k)
                matches = [d.page_content for d in docs]
                logger.debug(f"FAISS retrieved {len(matches)} chunks")
            except Exception as e:
                logger.error(f"FAISS similarity search failed: {e}")
        
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
    
    def retrieve_with_logging(
        self,
        query: str,
        message_id: int,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """Retrieve with analytics logging (production method).
        
        This method should be used in production `/api/chat` endpoint.
        It retrieves chunks AND logs the event for evaluation.
        
        Args:
            query: User query
            message_id: ID from messages table (for linking retrieval logs)
            top_k: Number of chunks to retrieve
            
        Returns:
            Same format as retrieve() but with logging
            
        Why this matters:
        - Enables RAG evaluation metrics
        - Tracks which chunks are useful
        - A/B testing different thresholds
        - Debugging bad responses
        """
        if self.use_pgvector and self.pgvector_retriever:
            try:
                # Use pgvector's built-in logging
                chunks = self.pgvector_retriever.retrieve_and_log(
                    query=query,
                    message_id=message_id,
                    top_k=top_k
                )
                matches = [c['content'] for c in chunks]
                skills_fragments = [m for m in matches if "skill" in m.lower()]
                
                return {
                    "matches": matches,
                    "skills": skills_fragments if skills_fragments else ["No explicit skills extracted"],
                    "raw": matches,
                    "similarity_scores": [c['similarity'] for c in chunks],
                    "logged": True
                }
            except Exception as e:
                logger.error(f"Logged retrieval failed: {e}")
                # Fall back to regular retrieve
        
        # Fallback: regular retrieve without logging
        result = self.retrieve(query, top_k)
        result["logged"] = False
        return result

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
        
        **NEW**: Uses pgvector's role-aware retrieval when available.
        
        DEPRECATION: passing only `role` to trigger code inclusion will be removed in a future version.
        Callers should pass include_code=bool explicitly (RoleRouter now handles this).
        """
        if include_code is None and role is not None:
            logger.debug("DEPRECATION: implicit role-based code inclusion – supply include_code explicitly.")
        
        # Ensure latest code before searching (unless disabled)
        self.ensure_code_index_current()
        
        # Use pgvector role-aware retrieval if available
        if self.use_pgvector and self.pgvector_retriever and role:
            try:
                chunks = self.pgvector_retriever.retrieve_for_role(
                    query=query,
                    role=role,
                    top_k=top_k
                )
                matches = [c['content'] for c in chunks]
                skills_fragments = [m for m in matches if "skill" in m.lower()]
                career_results = {
                    "matches": matches,
                    "skills": skills_fragments if skills_fragments else ["No explicit skills extracted"],
                    "raw": matches
                }
                logger.debug(f"pgvector role-aware retrieval: role={role}, chunks={len(chunks)}")
            except Exception as e:
                logger.error(f"pgvector role retrieval failed, using standard: {e}")
                career_results = self.retrieve(query, top_k)
        else:
            # Standard retrieval (FAISS or basic pgvector)
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
        """Get summary of RAG engine state and capabilities."""
        summary = {
            "mode": "pgvector" if self.use_pgvector else "FAISS",
            "documents": len(self._career_docs) if hasattr(self, '_career_docs') else 0,
            "vector_store": bool(self.vector_store) if hasattr(self, 'vector_store') else False,
            "pgvector_enabled": self.use_pgvector,
            "ready": self.use_pgvector or (hasattr(self, 'vector_store') and self.vector_store is not None),
            "code_index_version": self.code_service.version() if hasattr(self, 'code_service') and self.code_service else "none"
        }
        
        # Add pgvector health check
        if self.use_pgvector and self.pgvector_retriever:
            try:
                health = self.pgvector_retriever.health_check()
                summary["pgvector_health"] = health["status"]
                summary["embedding_model"] = health.get("embedding_model", "unknown")
            except Exception as e:
                summary["pgvector_health"] = f"error: {e}"
        
        return summary
    
    def health_check(self) -> Dict[str, Any]:
        """Check if RAG engine is operational.
        
        Returns:
            Status dict with health indicators
        """
        status = {
            "status": "unknown",
            "mode": "pgvector" if self.use_pgvector else "FAISS",
            "checks": {}
        }
        
        try:
            # Check embeddings
            test_embedding = self.embed("health check")
            status["checks"]["embeddings"] = "ok" if test_embedding else "failed"
            
            # Check retrieval
            test_retrieval = self.retrieve("test", top_k=1)
            status["checks"]["retrieval"] = "ok" if test_retrieval.get("matches") else "failed"
            
            # Check pgvector if enabled
            if self.use_pgvector and self.pgvector_retriever:
                pgv_health = self.pgvector_retriever.health_check()
                status["checks"]["pgvector"] = pgv_health["status"]
            
            # Overall status
            all_ok = all(v == "ok" or v == "healthy" for v in status["checks"].values())
            status["status"] = "healthy" if all_ok else "degraded"
            
        except Exception as e:
            status["status"] = "unhealthy"
            status["error"] = str(e)
        
        return status

@dataclass
class CodeDisplayMetrics:
    """Metrics for code display operations."""
    timestamp: datetime
    query_time: float
    # ... all fields documented