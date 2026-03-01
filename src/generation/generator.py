from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
import json


class Generator:

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )

    # --------------------------------------------------
    # Load Prompt Strategy
    # --------------------------------------------------
    def load_prompt(self, strategy: str) -> str:
        path = os.path.join("prompts", f"{strategy}.txt")

        if not os.path.exists(path):
            raise ValueError(f"Prompt strategy '{strategy}' not found.")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # --------------------------------------------------
    # Format Context (Mejorado y Seguro)
    # --------------------------------------------------
    def format_context(self, context_chunks: list) -> str:

        if not context_chunks:
            return ""

        formatted_chunks = []

        for idx, chunk in enumerate(context_chunks):

            if isinstance(chunk, dict):
                text = chunk.get("document", "") or chunk.get("text", "")
                metadata = chunk.get("metadata", {}) or {}
                score = chunk.get("similarity_score")

            elif hasattr(chunk, "page_content"):
                text = chunk.page_content
                metadata = getattr(chunk, "metadata", {}) or {}
                score = getattr(chunk, "score", None)

            elif isinstance(chunk, str):
                text = chunk
                metadata = {}
                score = None

            else:
                continue

            title = metadata.get("title")
            authors = metadata.get("authors")
            year = metadata.get("year")

            score_text = f"Similarity: {score}\n" if score else ""

            formatted_chunks.append(
                f"[Source {idx + 1}]\n"
                f"{'Title: ' + title if title else ''}\n"
                f"{'Authors: ' + authors if authors else ''}\n"
                f"{'Year: ' + str(year) if year else ''}\n"
                f"{score_text}\n"
                f"{text}"
            )

        return "\n\n---\n\n".join(formatted_chunks)

    # --------------------------------------------------
    # APA Citations (Ahora NO genera basura)
    # --------------------------------------------------
    def format_apa_citations(self, context_chunks: list):

        citations = []
        citation_map = {}

        if not context_chunks:
            return citations, citation_map

        citation_counter = 1

        for chunk in context_chunks:

            if isinstance(chunk, dict):
                metadata = chunk.get("metadata", {}) or {}
            elif hasattr(chunk, "metadata"):
                metadata = getattr(chunk, "metadata", {}) or {}
            else:
                metadata = {}

            title = metadata.get("title")
            authors = metadata.get("authors")
            year = metadata.get("year")

            # 🚀 ONLY create citation if metadata is valid
            if not title or not authors or not year:
                continue

            citation_text = f"{authors} ({year}). {title}."

            citation_map[citation_counter] = citation_text
            citations.append(f"[{citation_counter}] {citation_text}")

            citation_counter += 1

        return citations, citation_map

    # --------------------------------------------------
    # Main Generate
    # --------------------------------------------------
    def generate(
        self,
        question: str,
        context_chunks: list,
        strategy: str = "v1_delimiters"
    ):

        # 🚀 If no context → avoid hallucination
        if not context_chunks:
            return {
                "answer": "No relevant documents found in the retrieved papers.",
                "citations": [],
                "citation_map": {}
            }

        template = self.load_prompt(strategy)

        context = self.format_context(context_chunks)

        try:
            final_prompt = template.format(
                question=question,
                context=context
            )
        except KeyError:
            final_prompt = (
                template +
                f"\n\nQuestion:\n{question}\n\nContext:\n{context}"
            )

        response = self.llm.invoke(
            [HumanMessage(content=final_prompt)]
        )

        answer = response.content

        # JSON strategy
        if "json" in strategy.lower():
            try:
                answer = json.loads(answer)
            except Exception:
                answer = {
                    "error": "Model did not return valid JSON.",
                    "raw_output": response.content
                }

        citations, citation_map = self.format_apa_citations(context_chunks)

        return {
            "answer": answer,
            "citations": citations,
            "citation_map": citation_map
        }