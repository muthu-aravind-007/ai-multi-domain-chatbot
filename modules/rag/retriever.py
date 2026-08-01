from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pathlib import Path
import hashlib

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

EMBEDDINGS_FILE = CACHE_DIR / "embeddings.npy"
HASH_FILE = CACHE_DIR / "documents.hash"


class VectorStore:
    def __init__(self, documents):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.documents = documents

        current_hash = self._compute_hash(documents)

        if (
            EMBEDDINGS_FILE.exists()
            and HASH_FILE.exists()
            and HASH_FILE.read_text() == current_hash
        ):
            print("✅ Loading cached embeddings...")
            self.embeddings = np.load(EMBEDDINGS_FILE)

        else:
            print("⚡ Generating embeddings...")
            self.embeddings = self.model.encode(
                documents,
                convert_to_numpy=True,
                show_progress_bar=True
            )

            np.save(EMBEDDINGS_FILE, self.embeddings)
            HASH_FILE.write_text(current_hash)

            print("✅ Embeddings cached successfully.")

    def search(self, query, k=5):
        query_vec = self.model.encode(
            [query],
            convert_to_numpy=True
        )

        similarities = cosine_similarity(query_vec, self.embeddings)[0]

        top_k_idx = np.argsort(similarities)[-k:][::-1]

        return [self.documents[i] for i in top_k_idx]

    @staticmethod
    def _compute_hash(documents):
        text = "\n".join(documents)
        return hashlib.md5(text.encode("utf-8")).hexdigest()