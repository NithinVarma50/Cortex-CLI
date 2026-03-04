import os
from typing import List

from langchain_core.language_models.chat_models import BaseChatModel


class ModelRouter:
    """Routes to the correct LLM provider based on model name."""

    def __init__(self):
        self.available_providers = ["openai", "anthropic", "groq", "ollama"]
        self.default_model = os.getenv("CORTEX_DEFAULT_MODEL", "gpt-4o")

    def get_model(self, model_name: str = None) -> BaseChatModel:
        """Get an initialized Langchain chat model instance."""
        target_model = model_name or self.default_model

        if target_model.startswith("gpt-"):
            from models.openai_model import get_openai_model
            return get_openai_model(target_model)
        elif target_model.startswith("claude-"):
            from models.anthropic_model import get_anthropic_model
            return get_anthropic_model(target_model)
        elif "mixtral" in target_model.lower() or "llama3-70b" in target_model.lower():
            from models.groq_model import get_groq_model
            return get_groq_model(target_model)
        else:
            # Fallback for ollama models like llama3, gemma, mistral, deepseek
            from models.ollama_model import get_ollama_model
            return get_ollama_model(target_model)

    def list_available(self) -> List[str]:
        return [
            "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo",
            "claude-3-5-sonnet", "claude-3-haiku",
            "llama3-70b", "mixtral-8x7b",
            "llama3", "mistral", "gemma", "deepseek"
        ]

    def test_connection(self, model_name: str) -> bool:
        """Test connection by sending a tiny ping message."""
        try:
            model = self.get_model(model_name)
            response = model.invoke("ping")
            return bool(response)
        except Exception:
            return False

    def set_default(self, model_name: str) -> None:
        """Set default model in active env."""
        os.environ["CORTEX_DEFAULT_MODEL"] = model_name
        self.default_model = model_name
