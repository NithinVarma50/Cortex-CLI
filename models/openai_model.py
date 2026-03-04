import os
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

def get_openai_model(model_name: str = "gpt-4o") -> BaseChatModel:
    """Initialize and return an OpenAI chat model."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is missing.")
    return ChatOpenAI(model=model_name, openai_api_key=api_key)
