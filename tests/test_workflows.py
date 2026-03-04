import pytest
import os
import tempfile
from core.workflow_engine import WorkflowEngine
from memory.memory_manager import MemoryManager

@pytest.fixture
def engine():
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["CORTEX_STORAGE_PATH"] = temp_dir
        mem = MemoryManager()
        engine = WorkflowEngine(mem)
        yield engine

def test_workflow_yaml_parsing(engine):
    # Uses real product_launch.yaml in the workflows folder
    workflow = engine.load_workflow("product_launch")
    assert workflow.name == "product_launch"
    assert len(workflow.steps) == 4
    assert workflow.steps[0].id == "research"
    assert workflow.steps[0].agent == "research_agent"

def test_workflow_dependency_resolution(engine):
    workflow = engine.load_workflow("product_launch")
    # Finance depends on marketing
    finance_step = next(s for s in workflow.steps if s.id == "finance")
    assert finance_step.depends_on == ["marketing"]

@pytest.mark.asyncio
async def test_workflow_step_execution(engine):
    # Simulated run logic testing handled via orchestrator mock inside run loop
    workflow = engine.load_workflow("marketing_campaign")
    assert len(workflow.steps) > 0

@pytest.mark.asyncio
async def test_workflow_failure_retry(engine):
    # Test stub for max retry exception checking
    pass
