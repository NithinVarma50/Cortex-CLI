import os
import yaml
import asyncio
from typing import Dict, Any, List
from pydantic import BaseModel

from cli.display import show_spinner, print_success, print_error, print_info
from memory.memory_manager import MemoryManager


class WorkflowStep(BaseModel):
    id: str
    agent: str
    task: str
    output_key: str
    depends_on: List[str] = []


class WorkflowDef(BaseModel):
    name: str
    description: str
    version: str
    steps: List[WorkflowStep]
    output: Dict[str, str]


class WorkflowEngine:
    """Executes multi-agent workflows defined in YAML."""

    def __init__(self, memory_manager: MemoryManager, orchestrator=None):
        self.memory = memory_manager
        self.orchestrator = orchestrator  # Will be injected to avoid circular imports
        self.workflows_path = os.getenv("CORTEX_WORKFLOWS_PATH", os.path.join(os.getcwd(), "workflows"))

    def load_workflow(self, name: str) -> WorkflowDef:
        path = os.path.join(self.workflows_path, f"{name}.yaml")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Workflow '{name}.yaml' not found in {self.workflows_path}")
            
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        steps = [WorkflowStep(**step) for step in data.get("steps", [])]
        return WorkflowDef(
            name=data["name"],
            description=data["description"],
            version=str(data.get("version", "1.0.0")),
            steps=steps,
            output=data.get("output", {})
        )

    async def execute_step(self, step: WorkflowStep, context: Dict[str, str], run_id: str) -> str:
        """Executes a single step with retry logic."""
        max_retries = 3
        # In a real LangGraph setup, this would be a node function.
        # We manually simulate the retry loop for simplicity and direct control over Rich output.
        
        # Inject inputs into task template
        task_prompt = step.task
        for key, val in context.items():
            if f"{{{key}}}" in task_prompt:
                task_prompt = task_prompt.replace(f"{{{key}}}", val)
                
        self.memory.history.log_task(step.id, run_id, step.agent, task_prompt)
        
        for attempt in range(1, max_retries + 1):
            try:
                # Use orchestrator to run task
                if self.orchestrator:
                    result = await self.orchestrator.run_agent_task(step.agent, task_prompt)
                else:
                    # Fallback stub
                    await asyncio.sleep(1)
                    result = f"[Mock output for {step.agent} on task: {task_prompt}]"
                    
                self.memory.history.update_task_result(step.id, "completed", result)
                return result
            except Exception as e:
                print_error(f"Error in step '{step.id}' attempt {attempt}: {str(e)}")
                if attempt == max_retries:
                    self.memory.history.update_task_result(step.id, "failed", str(e))
                    raise RuntimeError(f"Step {step.id} failed after {max_retries} retries.")
                await asyncio.sleep(2)

    async def run(self, name: str, initial_context: str = None) -> Dict[str, Any]:
        workflow = self.load_workflow(name)
        run_id = f"run_{name}_{os.urandom(4).hex()}"
        
        self.memory.history.create_workflow_run(run_id, workflow.name)
        print_info(f"Starting workflow: {workflow.name} (Run ID: {run_id})")
        
        context = {"input": initial_context} if initial_context else {}
        completed_steps = set()
        step_outputs = {}
        
        # Build dependency graph
        pending_steps = {s.id: s for s in workflow.steps}
        
        with show_spinner(f"Executing workflow DAG..."):
            while pending_steps:
                # Find steps whose dependencies are met
                ready_steps = []
                for step_id, step in pending_steps.items():
                    if all(dep in completed_steps for dep in step.depends_on):
                        ready_steps.append(step)
                
                if not ready_steps:
                    self.memory.history.update_workflow_run(run_id, "failed")
                    raise RuntimeError("Deadlock detected in workflow dependencies!")
                
                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    tasks.append(self.execute_step(step, context, run_id))
                    
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for step, result in zip(ready_steps, results):
                    if isinstance(result, Exception):
                        self.memory.history.update_workflow_run(run_id, "failed")
                        raise result
                        
                    step_outputs[step.id] = result
                    context[step.output_key] = result
                    completed_steps.add(step.id)
                    del pending_steps[step.id]
                    
        self.memory.history.update_workflow_run(run_id, "completed")
        print_success(f"Workflow '{workflow.name}' completed successfully.")
        
        return {
            "run_id": run_id,
            "outputs": step_outputs,
            "final_context": context
        }
