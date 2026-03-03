from src.retrieval.retriever import Retriever
from src.generation.generator import Generator
import json
import os
import re


class RAGPipeline:
    """
    Main orchestrator:
    - Metadata Router (improved, less aggressive)
    - Retrieval
    - Generation
    """

    def __init__(self):
        self.retriever = Retriever()
        self.generator = Generator()

    # ==========================================================
    # 🔎 SMART METADATA ROUTER (Only explicit listing requests)
    # ==========================================================
    def is_metadata_query(self, question: str) -> bool:

        q = question.lower()

        metadata_patterns = [
            # English - only explicit listing/enumeration requests
            r"\blist (all |the |my )?(papers|titles|authors|documents)\b",
            r"\bshow (all |the |my )?(papers|titles|authors|documents)\b",
            r"\bwhat (papers|titles|documents) (do you have|are available|are indexed)\b",
            r"\bhow many papers\b",
            r"\ball (the |my )?papers\b",
            r"\ball (the |my )?titles\b",
            r"\ball (the |my )?authors\b",
            r"\blist of papers\b",
            r"\blist of titles\b",

            # Spanish - only explicit listing requests
            r"\blistar (los |mis )?papers\b",
            r"\blistar (los |mis )?títulos\b",
            r"\bcuántos papers\b",
            r"\bqué papers (tienes|hay|están)\b",
            r"\bqué investigaciones (tienes|hay|están)\b",
            r"\btodos los papers\b",
            r"\btodos los títulos\b",
            r"\blista de papers\b",
            r"\blista de títulos\b",
        ]

        for pattern in metadata_patterns:
            if re.search(pattern, q):
                return True

        return False

    # ==========================================================
    # 📂 Metadata Handler
    # ==========================================================
    def handle_metadata_query(self):

        try:
            catalog_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "papers",
                "paper_catalog.json"
            )

            catalog_path = os.path.abspath(catalog_path)

            if not os.path.exists(catalog_path):
                return "Catalog file not found.", []

            with open(catalog_path, "r", encoding="utf-8") as f:
                catalog = json.load(f)

            papers = catalog.get("papers", [])

            if not papers:
                return "No papers found in catalog.", []

            lines = []
            for i, paper in enumerate(papers, 1):
                title = paper.get("title", "Unknown Title")
                authors = paper.get("authors", [])
                year = paper.get("year", "N/A")
                author_str = ", ".join(authors[:2]) + (" et al." if len(authors) > 2 else "")
                lines.append(f"{i}. **{title}** — {author_str} ({year})")

            formatted = "\n".join(lines)
            return formatted, []

        except Exception as e:
            return f"Error reading catalog: {str(e)}", []

    # ==========================================================
    # 🔄 Normal Retrieval (Robust Parsing)
    # ==========================================================
    def _parse_retrieval_results(self, results):

        retrieved_chunks = []

        if not results:
            return retrieved_chunks

        # CASE 1: Retriever returns list directly
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict):
                    retrieved_chunks.append({
                        "document": item.get("document") or item.get("text"),
                        "metadata": item.get("metadata", {})
                    })
            return retrieved_chunks

        # CASE 2: Retriever returns dict (Chroma style)
        if isinstance(results, dict):
            documents_list = results.get("documents", [])
            metadatas_list = results.get("metadatas", [])

            documents = documents_list[0] if (
                documents_list and isinstance(documents_list[0], list)
            ) else documents_list

            metadatas = metadatas_list[0] if (
                metadatas_list and isinstance(metadatas_list[0], list)
            ) else metadatas_list

            for i, doc in enumerate(documents):
                retrieved_chunks.append({
                    "document": doc,
                    "metadata": metadatas[i] if i < len(metadatas) else {}
                })

        return retrieved_chunks

    # ==========================================================
    # 🚀 Query Pipeline
    # ==========================================================
    def query(self, question: str, strategy: str = "v1_delimiters"):

        # 1️⃣ Metadata Shortcut (only for explicit listing queries)
        if self.is_metadata_query(question):
            answer_text, citations = self.handle_metadata_query()
            return {
                "question": question,
                "answer": answer_text,
                "citations": citations,
                "citation_map": {},
                "retrieved_chunks": []
            }

        # 2️⃣ Retrieval
        results = self.retriever.retrieve(question)
        retrieved_chunks = self._parse_retrieval_results(results)

        # 3️⃣ Generation
        answer_data = self.generator.generate(
            question,
            retrieved_chunks,
            strategy=strategy
        )

        return {
            "question": question,
            "answer": answer_data.get("answer"),
            "citations": answer_data.get("citations", []),
            "citation_map": answer_data.get("citation_map", {}),
            "retrieved_chunks": retrieved_chunks
        }
