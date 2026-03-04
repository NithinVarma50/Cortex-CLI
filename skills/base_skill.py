from typing import Any, Dict


class BaseSkill:
    """Base class for all Cortex skills."""
    name: str = "base_skill"
    description: str = "Base skill description"
    version: str = "1.0.0"

    def execute(self, input_text: str, **kwargs) -> str:
        """Execute the skill logic."""
        raise NotImplementedError

    def validate_input(self, input_text: str) -> bool:
        """Validate the skill input."""
        return isinstance(input_text, str) and len(input_text.strip()) > 0

    def get_schema(self) -> Dict[str, Any]:
        """Return a schema definition for LLM tool binding."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "input_text": {
                        "type": "string",
                        "description": "The input to the skill.",
                    }
                },
                "required": ["input_text"],
            },
        }
