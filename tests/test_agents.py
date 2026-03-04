import pytest
from agents.finance_agent import FinanceAgent
from agents.marketing_agent import MarketingAgent

def test_agent_creation():
    agent = FinanceAgent()
    assert agent.name == "finance_agent"
    assert "spreadsheet_analyzer" in agent.skills
    assert "file_reader" in agent.skills

def test_agent_memory_access():
    agent = MarketingAgent()
    assert agent.memory_access is True

@pytest.mark.asyncio
async def test_agent_run_task():
    # Mock orchestrator behavior testing via basic task template
    agent = FinanceAgent()
    prompt = agent.get_prompt_template()
    assert "Senior Financial Analyst" in prompt
    assert "Analyze financial data" in prompt

def test_agent_skill_assignment():
    agent = FinanceAgent()
    agent.skills.append("code_executor")
    assert "code_executor" in agent.skills
    assert len(agent.skills) == 3
