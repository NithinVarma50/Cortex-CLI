import os
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

def get_groq_model(model_name: str = "llama3-70b-8192") -> BaseChatModel:
    """Initialize and return a Groq chat model."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing.")
    return ChatGroq(model_name=model_name, groq_api_key=api_key)
