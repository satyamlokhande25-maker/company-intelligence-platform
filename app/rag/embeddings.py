from sentence_transformers import SentenceTransformer

class Embedder:
    """
    Handles local embeddings generation using Sentence Transformers.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: list[str]):
        return self.model.encode(texts, convert_to_numpy=True)