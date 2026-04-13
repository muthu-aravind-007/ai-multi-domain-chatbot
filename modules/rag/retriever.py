from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class VectorStore:
    def __init__(self, documents):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.documents = documents

        self.embeddings = self.model.encode(documents)

    def search(self, query, k=5):
        query_vec = self.model.encode([query])

        similarities = cosine_similarity(query_vec, self.embeddings)[0]

        top_k_idx = np.argsort(similarities)[-k:][::-1]

        results = [self.documents[i] for i in top_k_idx]

        return results