from core.rag.loader import load_rules
from core.rag.cleaner import clean_text
from core.rag.chunker import chunk_text
from core.rag.embedder import Embedder
from core.rag.vector_store import VectorStore
from core.rag.retriever import Retriever


RULES_PATH = "data/rules/demo_rules.txt"


# Load + preprocess
raw = load_rules(RULES_PATH)
cleaned = clean_text(raw)
chunks = chunk_text(cleaned)

print("Chunks:", len(chunks))


# Embeddings
embedder = Embedder()
vectors = embedder.embed(chunks)

print("Embedding dim:", len(vectors[0]))


# Vector store
store = VectorStore(dim=len(vectors[0]))
store.add(vectors)


# Retriever
retriever = Retriever(embedder, store, chunks)


# Query
query = "Where should Tier 1 capital be reported?"

results = retriever.retrieve(query)

print("\nQuery:", query)
print("\nRetrieved Rules:")

for r in results:
    print("-", r)
