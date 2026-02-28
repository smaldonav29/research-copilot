import re


def clean_extracted_text(text: str) -> str:
    """
    Clean and normalize extracted PDF text.
    Handles whitespace, hyphen breaks, and artifacts.
    """

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Fix broken hyphen words
    text = re.sub(r"(\w+)-\s+(\w+)", r"\1\2", text)

    # Remove isolated page numbers
    text = re.sub(r"\n\d+\n", "\n", text)

    return text.strip()