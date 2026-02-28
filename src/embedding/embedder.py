from openai import OpenAI


class OpenAIEmbedder:
    """
    Generate embeddings using OpenAI embedding models.
    """

    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = OpenAI()
        self.model = model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )

        return [item.embedding for item in response.data]

    def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a single query.
        """

        return self.embed_texts([query])[0]