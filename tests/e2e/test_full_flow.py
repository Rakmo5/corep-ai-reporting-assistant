import json

from core.rag.loader import load_rules
from core.rag.cleaner import clean_text
from core.rag.chunker import chunk_text
from core.rag.embedder import Embedder
from core.rag.vector_store import VectorStore
from core.rag.retriever import Retriever
from core.agent.reporting_agent import ReportingAgent
from core.validators.corep_validator import CorepValidator


def test_full_pipeline():

    # Build RAG
    raw = load_rules("data/rules/demo_rules.txt")
    cleaned = clean_text(raw)
    chunks = chunk_text(cleaned)

    embedder = Embedder()
    vectors = embedder.embed(chunks)

    store = VectorStore(dim=len(vectors[0]))
    store.add(vectors)

    retriever = Retriever(embedder, store, chunks)

    # Schema
    with open("core/schemas/c01_schema.json") as f:
        schema = json.load(f)

    # Agent
    agent = ReportingAgent(retriever, schema)

    # Validator
    validator = CorepValidator(schema)

    # Input
    data = {
        "tier1": 100,
        "tier2": 50,
        "currency": "GBP"
    }

    result, errors = agent.run_with_retry(data, validator)

    assert not errors
    assert result["fields"]["r030"] == 150
