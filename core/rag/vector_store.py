import numpy as np


class VectorStore:
    """
    Simple in-memory vector store using cosine similarity.
    """

    def __init__(self, dim: int):

        self.dim = dim
        self.vectors = []

    def add(self, vectors):

        self.vectors.extend(vectors)

    def search(self, query_vec, top_k: int = 5):
        """
        Returns indices of top_k most similar vectors.
        """

        sims = []

        for i, vec in enumerate(self.vectors):

            sim = np.dot(query_vec, vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(vec) + 1e-8
            )

            sims.append((i, sim))

        # Sort by similarity (descending)
        sims.sort(key=lambda x: x[1], reverse=True)

        # Return top_k indices
        return [i for i, _ in sims[:top_k]]
