from core.rag.loader import load_rules
from core.rag.cleaner import clean_text
from core.rag.chunker import chunk_text


RULES_PATH = "data/rules/demo_rules.txt"


raw = load_rules(RULES_PATH)
print("RAW:\n", raw)

cleaned = clean_text(raw)
print("\nCLEANED:\n", cleaned)

chunks = chunk_text(cleaned)

print("\nCHUNKS:")
for i, c in enumerate(chunks):
    print(f"\nChunk {i+1}:")
    print(c)
