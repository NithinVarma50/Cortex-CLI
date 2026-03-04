from pydantic import Field
from agents.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    name: str = "research_agent"
    role: str = "Research Specialist"
    goal: str = "Deep research, summarize findings, market research"
    backstory: str = "Curious and thorough investigative researcher."
    model: str = "llama3-70b-8192"
    skills: list[str] = Field(default_factory=lambda: ["web_search", "file_reader"])
