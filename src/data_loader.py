import os
import pickle
from typing import Dict, List, Any, Optional
import faiss
import numpy as np
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import streamlit as st
import pandas as pd

class DataLoader:
    """Handles document loading, indexing, and retrieval using FAISS"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.index = None
        self.documents = []
        self.index_path = "faiss_index"
        self.metadata_path = "faiss_metadata.pkl"
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample Noah-related data"""
        
        sample_docs = [
            {
                "content": """Noah is a skilled software engineer with expertise in Python, JavaScript, and AI technologies. 
                He has experience with frameworks like Django, React, and Streamlit. Noah is passionate about 
                creating intelligent applications that solve real-world problems.""",
                "metadata": {"type": "resume", "section": "summary", "file": "noah_resume.pdf", "line": 1}
            },
            {
                "content": """Technical Skills:
                - Programming Languages: Python, JavaScript, TypeScript, Java
                - Web Frameworks: Django, FastAPI, React, Streamlit
                - AI/ML: LangChain, OpenAI APIs, FAISS, scikit-learn
                - Databases: PostgreSQL, MongoDB, Redis
                - Cloud: AWS, Docker, Kubernetes
                - Tools: Git, CI/CD, Linux""",
                "metadata": {"type": "resume", "section": "skills", "file": "noah_resume.pdf", "line": 15}
            },
            {
                "content": """Project: AI-Powered Chatbot
                - Built role-adaptive chatbot using Streamlit and LangChain
                - Implemented FAISS vector search for document retrieval
                - Integrated OpenAI GPT models for natural language processing
                - Added citation system with file:line references
                - Deployed on AWS with Docker containerization""",
                "metadata": {"type": "resume", "section": "projects", "file": "noah_resume.pdf", "line": 25}
            },
            {
                "content": """Fun Facts about Noah:
                - Loves MMA and follows UFC events religiously
                - Enjoys coding late at night with lo-fi music
                - Has a collection of mechanical keyboards
                - Drinks way too much coffee (seriously, it's a problem)
                - Once debugged code for 14 hours straight and called it 'fun'
                - Believes pineapple on pizza is actually great (fight me)""",
                "metadata": {"type": "fun_facts", "section": "personal", "file": "noah_facts.md", "line": 1}
            },
            {
                "content": """Noah's GitHub Repositories:
                - NoahsAIAssistant: Role-adaptive AI chatbot with Streamlit
                - DataPipeline: ETL framework for processing large datasets  
                - WebScraper: Async web scraping tool with rate limiting
                - APIGateway: Microservices gateway with authentication
                - MLOps: Machine learning deployment and monitoring tools""",
                "metadata": {"type": "code", "section": "repositories", "file": "github_projects.md", "line": 1}
            }
        ]
        
        # Convert to LangChain documents
        self.documents = [
            Document(page_content=doc["content"], metadata=doc["metadata"])
            for doc in sample_docs
        ]
        
        # Build or load FAISS index
        self._build_or_load_index()
    
    def _build_or_load_index(self):
        """Build FAISS index or load existing one"""
        
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                # Load existing index
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, 'rb') as f:
                    self.documents = pickle.load(f)
                st.success("Loaded existing FAISS index")
                return
            except Exception as e:
                st.warning(f"Failed to load existing index: {e}. Building new one...")
        
        # Build new index
        self._build_index()
    
    def _build_index(self):
        """Build FAISS index from documents"""
        
        try:
            # Extract text content
            texts = [doc.page_content for doc in self.documents]
            
            # Generate embeddings
            with st.spinner("Building FAISS index..."):
                embeddings_list = self.embeddings.embed_documents(texts)
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings_list, dtype=np.float32)
            
            # Build FAISS index
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings_array)
            
            # Save index and metadata
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.documents, f)
            
            st.success(f"Built FAISS index with {len(self.documents)} documents")
            
        except Exception as e:
            st.error(f"Error building FAISS index: {e}")
            self.index = None
    
    def search_documents(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant documents using FAISS"""
        
        if not self.index:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Search FAISS index
            distances, indices = self.index.search(query_array, k)
            
            # Prepare results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.documents):
                    doc = self.documents[idx]
                    results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "similarity_score": 1 / (1 + distance),  # Convert distance to similarity
                        "rank": i + 1
                    })
            
            return results
            
        except Exception as e:
            st.error(f"Error searching documents: {e}")
            return []
    
    def get_relevant_context(self, query: str, role: str = None) -> str:
        """Get relevant context for AI response generation"""
        
        # Search for relevant documents
        results = self.search_documents(query, k=3)
        
        if not results:
            return ""
        
        # Filter results based on role if specified
        if role:
            filtered_results = []
            for result in results:
                metadata = result["metadata"]
                
                # Role-specific filtering
                if role == "nontechnical_hiring" and metadata.get("type") == "resume":
                    filtered_results.append(result)
                elif role in ["technical_manager", "developer"] and metadata.get("type") in ["resume", "code"]:
                    filtered_results.append(result)
                elif role == "casual" and metadata.get("type") == "fun_facts":
                    filtered_results.append(result)
                else:
                    filtered_results.append(result)  # Include all for other roles
            
            results = filtered_results[:2]  # Limit to top 2 for role-specific
        
        # Build context string
        context_parts = []
        for result in results:
            context_parts.append(f"Source: {result['metadata']['file']}:{result['metadata']['line']}")
            context_parts.append(result["content"])
            context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Add a new document to the index"""
        
        try:
            # Create new document
            new_doc = Document(page_content=content, metadata=metadata)
            self.documents.append(new_doc)
            
            # Rebuild index with new document
            self._build_index()
            return True
            
        except Exception as e:
            st.error(f"Error adding document: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the FAISS index"""
        
        return {
            "total_documents": len(self.documents),
            "index_size": self.index.ntotal if self.index else 0,
            "document_types": list(set(doc.metadata.get("type", "unknown") for doc in self.documents)),
            "index_exists": self.index is not None
        }