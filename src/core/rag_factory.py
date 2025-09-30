"""RagEngine Component Factory

Handles the complex initialization logic for RagEngine components.
Separates construction concerns from core RAG orchestration.
"""
from __future__ import annotations

import logging
from typing import Optional, Tuple, Any
from pathlib import Path

from .langchain_compat import OpenAIEmbeddings, FAISS, ChatOpenAI, RetrievalQA
from .document_processor import DocumentProcessor
from .response_generator import ResponseGenerator

logger = logging.getLogger(__name__)

class RagEngineFactory:
    def __init__(self, settings=None):
        self.settings = settings
        self.degraded_mode = False
        self._faiss_ok = True

    def create_embeddings(self) -> Tuple[Any, bool]:
        """Create embeddings with fallback. Returns (embeddings, is_degraded)."""
        try:
            embeddings = OpenAIEmbeddings(
                openai_api_key=getattr(self.settings, "openai_api_key", None),
                model=getattr(self.settings, "embedding_model", "text-embedding-ada-002")
            )
            return embeddings, False
        except Exception as e:
            logger.warning(f"Embedding initialization failed, entering degraded mode: {e}")
            class _FallbackEmb:
                def embed_query(self, text: str):
                    return [float((hash(text) >> i) & 0xFF) / 255.0 for i in range(0, 32)]
            return _FallbackEmb(), True

    def create_llm(self) -> Tuple[Any, bool]:
        """Create LLM with fallback. Returns (llm, is_degraded)."""
        try:
            llm = ChatOpenAI(
                openai_api_key=getattr(self.settings, "openai_api_key", None),
                model_name=getattr(self.settings, "openai_model", "gpt-3.5-turbo"),
                temperature=0.4
            )
            return llm, False
        except Exception as e:
            logger.warning(f"LLM initialization failed, degraded mode responses will be used: {e}")
            class _FallbackLLM:
                def predict(self, prompt: str):
                    words = prompt.strip().split()
                    tail = " ".join(words[-40:])
                    return f"[DEGRADED MODE SYNTHESIS]\n{tail}"
            return _FallbackLLM(), True

    def create_career_kb(self, provided_kb=None):
        """Create or use provided career knowledge base."""
        if provided_kb is not None:
            return provided_kb
        
        try:
            from src.retrieval.career_kb import CareerKnowledgeBase
            kb_path = getattr(self.settings, "career_kb_path", "data/career_kb.csv")
            return CareerKnowledgeBase(kb_path)
        except Exception as e:
            logger.warning(f"Failed to create career KB: {e}")
            return None

    def create_code_index(self, provided_index=None):
        """Create or use provided code index."""
        if provided_index is not None:
            return provided_index
            
        try:
            from src.retrieval.code_index import CodeIndex
            index_path = getattr(self.settings, "code_index_path", "vector_stores/code_index")
            return CodeIndex(index_path)
        except Exception as e:
            logger.warning(f"Failed to create code index: {e}")
            return None

    def create_vector_store(self, documents, embeddings):
        """Create FAISS vector store with fallback."""
        if not documents:
            return None, False
            
        try:
            vector_store = FAISS.from_documents(documents, embeddings)
            self._persist_vector_store(vector_store)
            return vector_store, True
        except Exception as e:
            logger.warning(f"FAISS unavailable or build failed, degraded retrieval: {e}")
            return self._try_load_existing_store(embeddings)

    def _persist_vector_store(self, vector_store):
        """Persist vector store to disk."""
        try:
            faiss_path = Path("vector_stores/career_faiss")
            faiss_path.parent.mkdir(parents=True, exist_ok=True)
            vector_store.save_local(str(faiss_path))
        except Exception as e:
            logger.warning(f"Could not persist FAISS index: {e}")

    def _try_load_existing_store(self, embeddings):
        """Try to load existing FAISS store."""
        faiss_path = Path("vector_stores/career_faiss")
        if faiss_path.exists():
            try:
                vector_store = FAISS.load_local(
                    str(faiss_path),
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                return vector_store, True
            except Exception as e:
                logger.warning(f"Failed to load existing FAISS store: {e}")
        return None, False

    def create_qa_chain(self, llm, vector_store, response_generator):
        """Create RetrievalQA chain if possible."""
        if not vector_store or not self._faiss_ok or self.degraded_mode:
            return None
            
        try:
            prompt = response_generator.build_basic_prompt()
            return RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
        except Exception as e:
            logger.warning(f"QA chain creation failed: {e}")
            return None

    def load_documents(self, career_kb, provided_career_kb=None):
        """Load and process documents."""
        processor = DocumentProcessor(chunk_size=600, chunk_overlap=60)
        
        if provided_career_kb is not None:
            return processor.load_from_career_kb(provided_career_kb)
        
        kb_path = getattr(self.settings, "career_kb_path", "data/career_kb.csv")
        return processor.load_from_csv(kb_path, source_column="Question")
