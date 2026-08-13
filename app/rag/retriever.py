import os
from groq import Groq
from .document_builder import load_company_documents
from .chunker import chunk_documents
from .embeddings import Embedder
from .vector_store import InMemoryVectorStore

class RAGPipeline:
    def __init__(self, json_path: str = "output/company_profile.json"):
        self.embedder = Embedder()
        self.vector_store = InMemoryVectorStore()
        self.json_path = json_path
        self._build_pipeline()
        
        # Safe Initialization: Fetch key from Environment Variables
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is missing!")
            
        self.groq_client = Groq(api_key=api_key)

    def _build_pipeline(self):
        raw_docs = load_company_documents(self.json_path)
        chunks = chunk_documents(raw_docs)
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedder.generate_embeddings(texts)
        self.vector_store.add_documents(chunks, embeddings)

    def query(self, user_query: str, top_k: int = 3) -> dict:
        query_emb = self.embedder.generate_embeddings([user_query])[0]
        results = self.vector_store.search(query_emb, top_k=top_k)
        
        # Merge retrieved context
        context_text = "\n\n".join([r["document"]["text"] for r in results])

        # Strict Prompt to Stop Hallucinations
        system_prompt = (
            "You are an accurate Enterprise AI Assistant. "
            "Answer the question strictly based ONLY on the provided context. "
            "If the answer is not mentioned in the context (e.g. CEO/Founder name is missing), "
            "explicitly state: 'Information not available in the company profile.' Do not make up facts."
        )

        user_content = f"Context:\n{context_text}\n\nQuestion: {user_query}"

        # Fast Inference using Llama 3.3 on Groq
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.1
        )
        
        return {
            "answer": response.choices[0].message.content,
            "sources": results
        }