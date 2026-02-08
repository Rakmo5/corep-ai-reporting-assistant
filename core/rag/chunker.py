from typing import List


def chunk_text(text: str) -> List[str]:
    """
    Split regulatory text by rules/paragraphs.
    Each rule becomes one chunk.
    """

    lines = text.split("\n")

    chunks = []

    current = ""

    for line in lines:

        if line.lower().startswith("rule") and current:
            chunks.append(current.strip())
            current = line
        else:
            current += " " + line

    if current:
        chunks.append(current.strip())

    return chunks
