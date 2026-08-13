import numpy as np

class InMemoryVectorStore:
    """
    In-memory vector storage with Cosine Similarity calculation.
    """
    def __init__(self):
        self.vectors = []
        self.documents = []

    def add_documents(self, documents: list[dict], embeddings: np.ndarray):
        for doc, emb in zip(documents, embeddings):
            norm_emb = emb / (np.linalg.norm(emb) + 1e-10)
            self.vectors.append(norm_emb)
            self.documents.append(doc)

    def search(self, query_vector: np.ndarray, top_k: int = 3) -> list[dict]:
        if not self.vectors:
            return []

        norm_query = query_vector / (np.linalg.norm(query_vector) + 1e-10)
        matrix = np.array(self.vectors)
        scores = np.dot(matrix, norm_query)

        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "document": self.documents[idx],
                "score": float(scores[idx])
            })
            
        return results