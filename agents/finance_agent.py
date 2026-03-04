from pydantic import Field
from agents.base_agent import BaseAgent


class FinanceAgent(BaseAgent):
    name: str = "finance_agent"
    role: str = "Senior Financial Analyst"
    goal: str = "Analyze financial data and provide actionable insights"
    backstory: str = "Expert financial analyst with 15 years of experience."
    model: str = "gpt-4o"
    skills: list[str] = Field(default_factory=lambda: ["spreadsheet_analyzer", "file_reader"])
