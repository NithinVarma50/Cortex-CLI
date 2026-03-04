from pydantic import Field
from agents.base_agent import BaseAgent


class LegalAgent(BaseAgent):
    name: str = "legal_agent"
    role: str = "Legal Advisor"
    goal: str = "Review contracts, identify risks, compliance checks"
    backstory: str = "Meticulous legal counsel with expertise in corporate law."
    model: str = "gpt-4o"
    skills: list[str] = Field(default_factory=lambda: ["file_reader", "web_search"])
