import re


def clean_text(text: str) -> str:
    """
    Clean raw regulatory text:
    - Remove extra spaces
    - Remove empty lines
    - Normalize formatting
    """

    # Remove multiple blank lines
    text = re.sub(r"\n\s*\n+", "\n", text)

    # Strip spaces from lines
    lines = [line.strip() for line in text.split("\n")]

    # Remove empty lines
    lines = [line for line in lines if line]

    return "\n".join(lines)
