from pydantic import Field
from agents.base_agent import BaseAgent


class MarketingAgent(BaseAgent):
    name: str = "marketing_agent"
    role: str = "Marketing Strategist"
    goal: str = "Create marketing strategy, copy, and competitive analysis"
    backstory: str = "Award-winning marketing strategist known for viral campaigns."
    model: str = "claude-3-5-sonnet-20240620"
    skills: list[str] = Field(default_factory=lambda: ["web_search", "file_reader"])
