from src.embedding.embedder import OpenAIEmbedder
from src.vectorstore.chroma_store import ChromaVectorStore


class Retriever:
    """
    Handles semantic search over vector database.
    """

    def __init__(self, collection_name: str = "papers"):
        self.embedder = OpenAIEmbedder()
        self.vectorstore = ChromaVectorStore()
        self.vectorstore.create_collection(collection_name)

    def retrieve(self, query: str, top_k: int = 5):
        """
        Convert query into embedding and search similar chunks.
        """

        query_embedding = self.embedder.embed_query(query)

        results = self.vectorstore.query(
            query_embedding=query_embedding,
            n_results=top_k
        )

        return results