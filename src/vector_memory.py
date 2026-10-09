"""
Vector Memory — RAG-style baseline.
Stores events as embeddings, retrieves by cosine similarity.
"""

from sentence_transformers import SentenceTransformer
from datetime import datetime
import numpy as np


class VectorMemory:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.contents = []        # raw text
        self.embeddings = []      # numpy vectors
        self.timestamps = []      # when stored

    def add(self, text: str):
        """Store a memory."""
        vec = self.model.encode(text, normalize_embeddings=True)
        self.embeddings.append(vec)
        self.contents.append(text)
        self.timestamps.append(datetime.now())
        print(f"[added] {text}")

    def query(self, question: str, top_k: int = 1):
        """Retrieve the top_k most similar memories."""
        if not self.embeddings:
            return []
        q_vec = self.model.encode(question, normalize_embeddings=True)
        matrix = np.vstack(self.embeddings)
        scores = matrix @ q_vec          # cosine sim (normalized)
        idx = np.argsort(-scores)[:top_k]
        return [(self.contents[i], float(scores[i]), self.timestamps[i]) for i in idx]


# --- Quick test ---
if __name__ == "__main__":
    mem = VectorMemory()
    mem.add("Alice is a Senior Software Engineer.")
    mem.add("Alice got promoted to Staff Engineer.")

    result = mem.query("What is Alice's current job title?")
    print("\nTop result:", result[0][0])
    print("Score:     ", result[0][1])