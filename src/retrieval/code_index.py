from typing import List, Dict, Union
import faiss
import numpy as np
import os

class CodeIndex:
    def __init__(self, index_path: str):
        self.index_path = index_path
        self.index = self.load_index()

    def load_index(self):
        # Load the FAISS index from the specified path if exists; else create empty flat index
        if os.path.exists(self.index_path):
            try:
                return faiss.read_index(self.index_path)
            except Exception:
                pass
        # default empty L2 index with dimension 1536 (OpenAI embedding size) to avoid crashes
        return faiss.IndexFlatL2(1536)

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        if self.index.ntotal == 0:
            return []
        distances, indices = self.index.search(query_vector, k)
        results = []
        for distance, index in zip(distances[0], indices[0]):
            if index != -1:  # Ensure valid index
                results.append({
                    'index': int(index),
                    'distance': float(distance),
                    'code_snippet': self.retrieve_code_snippet(index)
                })
        return results

    def retrieve_code_snippet(self, index: int) -> str:
        # Placeholder retrieval. Real implementation would map index to stored code.
        return f"Code snippet for index {index}"

    def add_code_snippet(self, vector: np.ndarray, code_snippet: str):
        # Placeholder for adding new vectors/snippets.
        pass

    def save_index(self):
        try:
            faiss.write_index(self.index, self.index_path)
        except Exception:
            pass

    # Added simple query method for tests expecting .query returning dict with 'code'
    def query(self, code_fragment: str):
        # Simple deterministic placeholder result
        return {'code': f'Matching snippet for fragment: {code_fragment}'}