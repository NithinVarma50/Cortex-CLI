import os
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

def get_anthropic_model(model_name: str = "claude-3-5-sonnet-20240620") -> BaseChatModel:
    """Initialize and return an Anthropic chat model."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is missing.")
    return ChatAnthropic(model=model_name, anthropic_api_key=api_key)
