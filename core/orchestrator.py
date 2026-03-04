import time
from langchain_core.messages import SystemMessage, HumanMessage

from core.task_router import TaskRouter
from memory.memory_manager import MemoryManager
from models.model_router import ModelRouter
from cli.display import console, print_info


class Orchestrator:
    """Central orchestrator that binds agents, Memory, and LLMs together."""

    def __init__(self, memory_manager: MemoryManager, model_router: ModelRouter):
        self.memory = memory_manager
        self.model_router = model_router
        self.task_router = TaskRouter()

    async def run_agent_task(self, agent_name: str, task: str) -> str:
        """Fully executes an agent task following the defined flow."""
        start_time = time.time()
        agent = self.task_router.get_agent(agent_name)
        
        # 1. Retrieve Context
        context = ""
        if agent.memory_access:
            context = self.memory.get_agent_context(agent_name, task)

        # 2. Construct Prompt
        sys_prompt = agent.get_prompt_template()
        if context:
            sys_prompt += f"\nRelevant Memory Context:\n{context}\n"
        sys_prompt += "\nOutput Format: Return the final, complete response formatted in Markdown."

        messages = [
            SystemMessage(content=sys_prompt),
            HumanMessage(content=f"Task:\n{task}")
        ]

        # 3. Execute LLM Call (Streaming)
        model = self.model_router.get_model(agent.model)
        
        # Try adjusting temperature if supported by setting it dynamically or using agent.temperature
        # Langchain ChatModels usually take temperature in constructor, but we'll use as-is for now.

        print_info(f"\n[Agent: {agent_name} | Model: {agent.model}] executing task...")
        console.print("─" * 40, style="dim white")
        
        full_response = ""
        try:
            # Stream output
            for chunk in model.stream(messages):
                console.print(chunk.content, end="")
                full_response += chunk.content
        except Exception as e:
            # Fallback if streaming is not supported by a specific provider wrapper
            response = model.invoke(messages)
            console.print(response.content)
            full_response = response.content
            
        console.print()
        console.print("─" * 40, style="dim white")

        duration = round(time.time() - start_time, 2)

        # 4. Save to Memory
        if agent.memory_access:
            # Save core result to company memory for future context
            self.memory.store(
                content=f"Task: {task}\nResult: {full_response}",
                memory_type="company",
                agent=agent_name
            )

        # 5. Log Execution
        self.memory.knowledge.log_event(
            "task_completed",
            f"Agent {agent_name} completed task in {duration}s."
        )

        return full_response
