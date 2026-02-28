from src.retrieval.retriever import Retriever
from src.generation.generator import Generator


class RAGPipeline:
    """
    Main orchestrator connecting:
    - Retrieval
    - Generation
    """

    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()

    def query(self, question: str):
        """
        Process user question through full RAG pipeline.
        """

        # 1. Retrieve relevant chunks
        results = self.retriever.retrieve(question)

        # 2. Extract documents from results
        retrieved_chunks = []

        if results and "documents" in results:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0] if results["metadatas"] else []

            for i, doc in enumerate(documents):
                chunk = {
                    "document": doc,
                    "metadata": metadatas[i] if i < len(metadatas) else {}
                }
                retrieved_chunks.append(chunk)

        # 3. Generate final answer
        answer = self.generator.generate(question, retrieved_chunks)

        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": retrieved_chunks
        }