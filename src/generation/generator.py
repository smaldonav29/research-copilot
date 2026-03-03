from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
import json


class Generator:
    """
    Generates answers using GPT-4o-mini with multiple prompt strategies.
    Handles context formatting, APA citations, JSON output,
    and optional debugging of retrieved metadata.
    """

    def __init__(self, debug: bool = False):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0
        )
        self.debug = debug

    # --------------------------------------------------
    # Load Prompt Strategy
    # --------------------------------------------------
    def load_prompt(self, strategy: str) -> str:
        path = os.path.join("prompts", f"{strategy}.txt")

        if not os.path.exists(path):
            raise ValueError(f"Prompt strategy '{strategy}' not found at {path}.")

        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # --------------------------------------------------
    # Debug Metadata (NEW)
    # --------------------------------------------------
    def _debug_metadata(self, context_chunks: list):
        if not self.debug:
            return

        print("\n🔎 DEBUG — Retrieved Context Metadata\n" + "-" * 50)

        for i, chunk in enumerate(context_chunks[:3]):  # limit to first 3
            metadata = chunk.get("metadata", {})
            print(f"\nSource {i + 1}:")
            print("Title  :", metadata.get("title"))
            print("Authors:", metadata.get("authors"))
            print("Year   :", metadata.get("year"))

        print("-" * 50 + "\n")

    # --------------------------------------------------
    # Format Context
    # --------------------------------------------------
    def format_context(self, context_chunks: list) -> str:

        if not context_chunks:
            return "No context available."

        formatted_chunks = []

        for idx, chunk in enumerate(context_chunks):

            if isinstance(chunk, dict):
                text = chunk.get("document", "") or chunk.get("text", "") or ""
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

            title   = metadata.get("title", "")
            authors = metadata.get("authors", "")
            year    = metadata.get("year", "")
            score_text = f"Similarity: {round(score, 3)}\n" if score else ""

            header_parts = []
            if title:
                header_parts.append(f"Title: {title}")
            if authors:
                header_parts.append(f"Authors: {authors}")
            if year:
                header_parts.append(f"Year: {year}")

            header = "\n".join(header_parts)

            formatted_chunks.append(
                f"[Source {idx + 1}]\n"
                f"{header}\n"
                f"{score_text}\n"
                f"{text.strip()}"
            )

        return "\n\n---\n\n".join(formatted_chunks)

    # --------------------------------------------------
    # APA Citations
    # --------------------------------------------------
    def format_apa_citations(self, context_chunks: list):

        citations = []
        citation_map = {}
        seen_titles = set()
        citation_counter = 1

        if not context_chunks:
            return citations, citation_map

        for chunk in context_chunks:

            metadata = chunk.get("metadata", {}) if isinstance(chunk, dict) else {}

            title   = metadata.get("title")
            authors = metadata.get("authors")
            year    = metadata.get("year")

            if not title or not authors or not year:
                continue
            if title in seen_titles:
                continue

            seen_titles.add(title)
            citation_text = f"{authors} ({year}). {title}."
            citation_map[citation_counter] = citation_text
            citations.append(f"[{citation_counter}] {citation_text}")
            citation_counter += 1

        return citations, citation_map

    # --------------------------------------------------
    # Parse JSON Answer safely
    # --------------------------------------------------
    def _parse_json_answer(self, raw: str) -> dict:
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        clean = clean.strip().rstrip("```").strip()

        try:
            return json.loads(clean)
        except Exception:
            return {
                "error": "Model did not return valid JSON.",
                "raw_output": raw
            }

    # --------------------------------------------------
    # Main Generate
    # --------------------------------------------------
    def generate(
        self,
        question: str,
        context_chunks: list,
        strategy: str = "v1_delimiters"
    ):
        if not context_chunks:
            return {
                "answer": (
                    "I could not find relevant information in the indexed papers "
                    "to answer your question. Please try rephrasing or ask about "
                    "a topic covered in the collection."
                ),
                "citations": [],
                "citation_map": {}
            }

        # 🔎 DEBUG HERE (before generation)
        self._debug_metadata(context_chunks)

        template = self.load_prompt(strategy)
        context  = self.format_context(context_chunks)

        try:
            final_prompt = template.format(
                question=question,
                context=context
            )
        except KeyError:
            final_prompt = (
                f"{template}\n\n"
                f"Question:\n{question}\n\n"
                f"Context:\n{context}"
            )

        response = self.llm.invoke(
            [HumanMessage(content=final_prompt)]
        )

        raw_answer = response.content

        if "json" in strategy.lower():
            answer = self._parse_json_answer(raw_answer)
        else:
            answer = raw_answer

        citations, citation_map = self.format_apa_citations(context_chunks)

        return {
            "answer": answer,
            "citations": citations,
            "citation_map": citation_map
        }