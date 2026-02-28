from openai import OpenAI
from src.config import load_config


class Generator:
    """
    Responsible for generating answers using GPT
    with retrieved context.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        config = load_config()
        self.client = OpenAI(api_key=config["openai_api_key"])
        self.model = model

    def build_prompt(self, question: str, context: str) -> str:
        """
        Construct prompt with retrieved context.
        """

        return f"""
You are an academic assistant.

Answer ONLY using the context provided.

If the answer is not in the context, say:
"I cannot find this information in the provided papers."

Always cite using APA format.

Context:
{context}

Question:
{question}

Answer:
"""

    def generate(self, question: str, retrieved_chunks: list):
        """
        Generate response using retrieved documents.
        """

        # Combine retrieved chunks into context
        context = "\n\n".join(
            [chunk["document"] if "document" in chunk else str(chunk)
             for chunk in retrieved_chunks]
        )

        prompt = self.build_prompt(question, context)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content