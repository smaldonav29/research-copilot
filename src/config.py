import os
from dotenv import load_dotenv


def load_config():
    """
    Load environment variables from .env
    """

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Please check your .env file."
        )

    return {
        "openai_api_key": api_key
    }