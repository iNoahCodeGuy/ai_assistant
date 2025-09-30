"""LangChain Compatibility Layer

Provides graceful fallbacks for LangChain imports to handle:
- Missing langchain-community package
- Version differences between langchain releases
- Development environments without full dependencies

This isolates import complexity from core RAG logic.
"""
from __future__ import annotations

import os
from typing import List, Any

# --- Resilient OpenAI Embeddings ---
try:
    from langchain_openai import OpenAIEmbeddings  # type: ignore
except Exception:
    try:
        from langchain.embeddings import OpenAIEmbeddings  # type: ignore
    except Exception:
        try:
            from langchain_community.embeddings import OpenAIEmbeddings  # type: ignore
        except Exception:
            class OpenAIEmbeddings:  # type: ignore
                def __init__(self, *_, **__):
                    pass
                def embed_query(self, text: str) -> List[float]:
                    return [float((hash(text) >> i) & 0xFF) / 255.0 for i in range(0, 32)]

# --- Resilient FAISS Vector Store ---
try:
    from langchain_community.vectorstores import FAISS  # type: ignore
except Exception:
    try:
        from langchain.vectorstores import FAISS  # type: ignore
    except Exception:
        class _StubVectorStore:
            def __init__(self, *_, **__):
                pass
            def similarity_search(self, *_, **__):
                return []
            def save_local(self, *_, **__):
                pass
            def as_retriever(self, *_, **__):
                class _StubRetriever:
                    def get_relevant_documents(self, *_, **__):
                        return []
                return _StubRetriever()
        
        class FAISS:  # type: ignore
            @staticmethod
            def from_documents(_docs, _emb):
                return None
            @staticmethod
            def load_local(*_, **__):
                return None

# --- Resilient Document Loaders ---
try:
    from langchain_community.document_loaders import CSVLoader  # type: ignore
except Exception:
    try:
        from langchain.document_loaders import CSVLoader  # type: ignore
    except Exception:
        class CSVLoader:  # type: ignore
            def __init__(self, file_path: str, source_column: str = "source"):
                self.file_path = file_path
                self.source_column = source_column
            def load(self):
                return []

# --- Resilient Text Splitter ---
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
except Exception:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
    except Exception:
        class RecursiveCharacterTextSplitter:  # type: ignore
            def __init__(self, chunk_size: int = 600, chunk_overlap: int = 60, **__):
                self.chunk_size = chunk_size
                self.chunk_overlap = chunk_overlap
            def split_documents(self, docs):
                return docs

# --- Resilient QA Chain ---
try:
    from langchain_community.chains import RetrievalQA  # type: ignore
except Exception:
    try:
        from langchain.chains import RetrievalQA  # type: ignore
    except Exception:
        class RetrievalQA:  # type: ignore
            @staticmethod
            def from_chain_type(*_, **__):
                return None

# --- Resilient Prompt Template ---
try:
    from langchain.prompts import PromptTemplate  # type: ignore
except Exception:
    try:
        from langchain_core.prompts import PromptTemplate  # type: ignore
    except Exception:
        class PromptTemplate:  # type: ignore
            def __init__(self, template: str, input_variables: List[str]):
                self.template = template
                self.input_variables = input_variables

# --- Resilient ChatOpenAI ---
try:
    from langchain_openai import ChatOpenAI  # type: ignore
except Exception:
    try:
        from langchain.chat_models import ChatOpenAI  # type: ignore
    except Exception:
        try:
            from langchain_community.chat_models import ChatOpenAI  # type: ignore
        except Exception:
            class ChatOpenAI:  # type: ignore
                def __init__(self, *_, **__):
                    pass
                def predict(self, prompt: str) -> str:
                    words = prompt.strip().split()
                    tail = " ".join(words[-40:])
                    return f"[DEGRADED MODE SYNTHESIS]\n{tail}"

# --- Document Schema ---
try:
    from langchain.schema import Document  # type: ignore
except Exception:
    try:
        from langchain_core.documents import Document  # type: ignore
    except Exception:
        class Document:  # type: ignore
            def __init__(self, page_content: str, metadata: dict = None):
                self.page_content = page_content
                self.metadata = metadata or {}

__all__ = [
    "OpenAIEmbeddings",
    "FAISS", 
    "CSVLoader",
    "RecursiveCharacterTextSplitter",
    "RetrievalQA",
    "PromptTemplate", 
    "ChatOpenAI",
    "Document"
]
