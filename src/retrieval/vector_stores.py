from typing import List, Any
import faiss
import numpy as np

class VectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.vectors = []
    
    def add_vectors(self, vectors: List[np.ndarray], metadata: List[Any] = None):
        """Add vectors to the FAISS index."""
        self.index.add(np.array(vectors).astype('float32'))
        self.vectors.extend(metadata if metadata else [None] * len(vectors))
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Any]:
        """Search for the top k nearest vectors to the query vector."""
        distances, indices = self.index.search(np.array([query_vector]).astype('float32'), k)
        return [(self.vectors[idx], distances[0][i]) for i, idx in enumerate(indices[0]) if idx < len(self.vectors)]

    def reset(self):
        """Reset the vector store."""
        self.index.reset()
        self.vectors = []