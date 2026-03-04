from typing import List, Optional
from pydantic import BaseModel, Field

# We will rely on memory_manager injected or imported later for memory_access.
# We will also use CrewAI's Agent definition indirectly, or build our own.
# Since Cortex is a custom multi-agent OS, we define our BaseAgent.


class BaseAgent(BaseModel):
    name: str = Field(..., description="The unique name of the agent")
    role: str = Field(..., description="The role the agent plays")
    goal: str = Field(..., description="The high-level goal of the agent")
    backstory: str = Field(..., description="Agent's backstory and persona")
    model: str = Field("gpt-4o", description="The LLM model used by this agent")
    skills: List[str] = Field(default_factory=list, description="List of skill names assigned")
    memory_access: bool = Field(True, description="Whether agent can access memories")
    temperature: float = Field(0.3, description="Model generation temperature")

    def run(self, task: str) -> str:
        """Execute a single task. This will be orchestrated by orchestrator.py."""
        raise NotImplementedError("run() is managed by the orchestrator in Cortex.")

    def load_skills(self) -> list:
        """Load skill plugin instances."""
        # TODO: Dynamically load skills from the skill manager
        return []

    def get_memory_context(self, query: str) -> str:
        """Retrieve context from the memory system."""
        # TODO: Call memory manager
        return ""

    def save_to_memory(self, content: str) -> None:
        """Save a new explicit memory."""
        # TODO: Call memory manager store
        pass

    def get_prompt_template(self) -> str:
        """Generate the system prompt for the agent."""
        return f"Role: {self.role}\nGoal: {self.goal}\nBackstory: {self.backstory}\n"

