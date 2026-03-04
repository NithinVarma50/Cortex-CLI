import os
import yaml
from typing import Dict, Any

from agents.base_agent import BaseAgent
from agents.finance_agent import FinanceAgent
from agents.marketing_agent import MarketingAgent
from agents.operations_agent import OperationsAgent
from agents.legal_agent import LegalAgent
from agents.research_agent import ResearchAgent

class TaskRouter:
    """Routes tasks to the correct agent based on configuration."""

    def __init__(self):
        self.config_path = os.getenv("CORTEX_CONFIG_PATH", os.path.join(os.getcwd(), "config"))
        self.agents_config = self._load_agents_config()
        self._agent_classes = {
            "finance_agent": FinanceAgent,
            "marketing_agent": MarketingAgent,
            "operations_agent": OperationsAgent,
            "legal_agent": LegalAgent,
            "research_agent": ResearchAgent
        }

    def _load_agents_config(self) -> Dict[str, Any]:
        path = os.path.join(self.config_path, "agents.yaml")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and "agents" in data:
                    return {a["name"]: a for a in data["agents"]}
        return {}

    def get_agent(self, agent_name: str) -> BaseAgent:
        """Instantiate and return the requested Agent configured from YAML."""
        if agent_name not in self._agent_classes:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        agent_cls = self._agent_classes[agent_name]
        
        # Override defaults with config if present
        config = self.agents_config.get(agent_name, {})
        
        return agent_cls(
            name=config.get("name", agent_name),
            role=config.get("role", agent_cls.__fields__["role"].default),
            goal=config.get("goal", agent_cls.__fields__["goal"].default),
            backstory=config.get("backstory", agent_cls.__fields__["backstory"].default),
            model=config.get("model", agent_cls.__fields__["model"].default),
            skills=config.get("skills", agent_cls.__fields__["skills"].default_factory()),
            memory_access=config.get("memory_access", True),
            temperature=config.get("temperature", 0.3)
        )

    def route_freeform_task(self, task: str) -> BaseAgent:
        """Uses an LLM (or simple keyword heuristics) to pick the best agent."""
        # For simplicity, we fallback to research_agent if not explicitly requested
        return self.get_agent("research_agent")
