from pydantic import Field
from agents.base_agent import BaseAgent


class OperationsAgent(BaseAgent):
    name: str = "operations_agent"
    role: str = "Operations Manager"
    goal: str = "Plan logistics, optimize processes, create SOPs, manage timelines"
    backstory: str = "Efficiency expert with a Six Sigma Black Belt."
    model: str = "gpt-4o"
    skills: list[str] = Field(default_factory=lambda: ["file_reader", "code_executor"])
