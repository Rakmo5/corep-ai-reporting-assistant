from pathlib import Path


def load_rules(file_path: str) -> str:
    """
    Load regulatory rules from a text file.
    Returns raw text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Rules file not found: {file_path}")

    if path.suffix.lower() != ".txt":
        raise ValueError("Only .txt files supported for now")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
