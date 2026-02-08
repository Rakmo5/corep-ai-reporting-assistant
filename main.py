import json

from core.rag.loader import load_rules
from core.rag.cleaner import clean_text
from core.rag.chunker import chunk_text
from core.rag.embedder import Embedder
from core.rag.vector_store import VectorStore
from core.rag.retriever import Retriever
from core.agent.reporting_agent import ReportingAgent
from core.validators.corep_validator import CorepValidator
from core.tools.report_saver import ReportSaver


def load_schema(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def build_retriever():

    rules_path = "data/rules/demo_rules.txt"

    raw = load_rules(rules_path)
    cleaned = clean_text(raw)
    chunks = chunk_text(cleaned)

    embedder = Embedder()
    vectors = embedder.embed(chunks)

    store = VectorStore(dim=len(vectors[0]))
    store.add(vectors)

    retriever = Retriever(embedder, store, chunks)

    return retriever


def main():

    # Build RAG
    retriever = build_retriever()

    # Load schema
    schema = load_schema("core/schemas/c01_schema.json")

    # Init agent  ✅ (THIS WAS MISSING)
    agent = ReportingAgent(retriever, schema)

    # Init validator
    validator = CorepValidator(schema)

    # Init saver
    saver = ReportSaver()
    
    # Example input
    user_data = {
        "tier1": 100,
        "tier2": 50,
        "currency": "GBP"
    }

    # Run agent with retry
    result, errors = agent.run_with_retry(user_data, validator)


    print("\n=== GENERATED REPORT ===\n")
    print(json.dumps(result, indent=2))

    # Validate
    errors = validator.validate(result)

    # Save report
    path = saver.save(result, errors)

    if errors:
        print("\n⚠️ VALIDATION ERRORS:\n")
        for e in errors:
            print("-", e)
    else:
        print("\n✅ Report passed validation")

    print(f"\n📁 Report saved to: {path}")

    

if __name__ == "__main__":
    main()
