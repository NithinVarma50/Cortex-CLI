from langchain_community.chat_models import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

def get_ollama_model(model_name: str = "llama3") -> BaseChatModel:
    """Initialize and return an Ollama chat model."""
    return ChatOllama(model=model_name)
