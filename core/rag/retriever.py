import numpy as np


class Retriever:
    """
    Retrieves relevant rule chunks using vector similarity.
    """

    def __init__(self, embedder, store, chunks):

        self.embedder = embedder
        self.store = store        # ✅ expose store
        self.chunks = chunks      # ✅ expose chunks

    def retrieve(self, query: str, top_k: int = 5):

        # Embed query
        query_vec = self.embedder.embed([query])[0]

        # Search vector store
        indices = self.store.search(query_vec, top_k=top_k)

        # Return matching chunks
        return [self.chunks[i] for i in indices]
