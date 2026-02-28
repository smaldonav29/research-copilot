import tiktoken


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

    def chunk_text(self, text: str, metadata: dict = None):
        """
        Split text into overlapping token chunks.
        Returns list of chunk dictionaries.
        """

        tokens = self.encoder.encode(text)
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "token_count": len(chunk_tokens),
                "metadata": metadata or {}
            })

            start += self.chunk_size - self.chunk_overlap
            chunk_id += 1

        return chunks