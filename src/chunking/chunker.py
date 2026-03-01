import tiktoken
import re


class TokenChunker:
    """
    Splits text into overlapping token chunks.
    Supports multiple chunk configurations.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        model: str = "gpt-4"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoder = tiktoken.encoding_for_model(model)

    # --------------------------------------------------
    # Clean unwanted paper sections BEFORE chunking
    # --------------------------------------------------
    def clean_text(self, text: str) -> str:

        if not text:
            return ""

        # Remove common useless academic sections
        cut_sections = [
            "references",
            "acknowledgments",
            "conflicts of interest",
            "data availability",
            "informed consent"
        ]

        lower_text = text.lower()

        for section in cut_sections:
            if section in lower_text:
                text = re.split(rf"\b{section}\b", text, flags=re.IGNORECASE)[0]

        # Clean excessive spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # --------------------------------------------------
    # Chunk text
    # --------------------------------------------------
    def chunk_text(self, text: str, metadata: dict = None):
        """
        Split text into overlapping token chunks.
        Returns list of chunk dictionaries.
        """

        if not text:
            return []

        # ✅ Clean text before chunking
        text = self.clean_text(text)

        if not text.strip():
            return []

        tokens = self.encoder.encode(text)

        chunks = []
        start = 0
        chunk_id = 0

        while start < len(tokens):

            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)

            if not chunk_text.strip():
                start += self.chunk_size - self.chunk_overlap
                continue

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "token_count": len(chunk_tokens),
                "metadata": metadata or {}
            })

            start += self.chunk_size - self.chunk_overlap
            chunk_id += 1

        return chunks