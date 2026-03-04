import os
import sys
import asyncio
import json
import typer

from cli.display import (
    print_banner,
    print_status,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_agent_list,
    print_generic_table,
    show_spinner,
)

from memory.memory_manager import MemoryManager
from models.model_router import ModelRouter
from core.orchestrator import Orchestrator
from core.workflow_engine import WorkflowEngine


app = typer.Typer(help="🧠 CORTEX — AI Operating System", no_args_is_help=True)

# Sub-groups
agent_app = typer.Typer(help="Manage AI agents")
workflow_app = typer.Typer(help="Manage and run workflows")
memory_app = typer.Typer(help="Manage short and long-term memory")
skill_app = typer.Typer(help="Manage agent skills")
model_app = typer.Typer(help="Manage LLM models")
config_app = typer.Typer(help="Manage system configuration")

app.add_typer(agent_app, name="agent")
app.add_typer(workflow_app, name="workflow")
app.add_typer(memory_app, name="memory")
app.add_typer(skill_app, name="skill")
app.add_typer(model_app, name="model")
app.add_typer(config_app, name="config")

# --- Dependencies ---
def get_memory() -> MemoryManager:
    return MemoryManager()

def get_router() -> ModelRouter:
    return ModelRouter()

def get_orchestrator() -> Orchestrator:
    return Orchestrator(get_memory(), get_router())

def get_workflow_engine() -> WorkflowEngine:
    return WorkflowEngine(get_memory(), get_orchestrator())


# Root commands
@app.command()
def init():
    """Initialize Cortex in current directory, reserve storage, create config."""
    print_banner()
    with show_spinner("Initializing Cortex runtime environment..."):
        os.makedirs("storage", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("config", exist_ok=True)
        
        # Touch DB and Vector
        mem = get_memory()
        
        # Record init event
        mem.knowledge.log_event("system_init", "Cortex framework initialized")
        
        # Insert default agents into Knowledge DB
        defaults = [
            ("finance_agent", "Senior Financial Analyst"),
            ("marketing_agent", "Marketing Strategist"),
            ("operations_agent", "Operations Manager"),
            ("legal_agent", "Legal Advisor"),
            ("research_agent", "Research Specialist")
        ]
        for name, role in defaults:
            mem.knowledge.insert_agent(name, role)
            
    print_success("Cortex initialized successfully!")
    print_info("Next steps:\n1. Check your .env config\n2. Run: cortex agent list\n3. Run: cortex agent run research_agent \"Research AI trends\"")


@app.command()
def start():
    """Start the Cortex daemon / interactive shell."""
    print_info("Interactive shell coming in future release.")


@app.command()
def status():
    """Show system status: agents, memory usage, active workflows."""
    print_banner()
    mem = get_memory()
    stats = mem.get_stats()
    router = get_router()
    
    print_status(
        agents_count=stats.get("agents_count", 0), 
        memory_used_mb=stats.get("total_storage_mb", 0), 
        memory_limit_gb=stats.get("limit_gb", 10), 
        default_model=router.default_model
    )


@app.command()
def reset(confirm: bool = typer.Option(False, "--confirm", help="Confirm memory wipe")):
    """Reset all memory and agents (with confirmation prompt)."""
    if not confirm:
        confirm = typer.confirm("Are you sure you want to completely wipe all cortex memory and agents?")
        if not confirm:
            print_info("Reset aborted.")
            raise typer.Abort()
            
    with show_spinner("Resetting system..."):
        get_memory().clear("all")
        
    print_success("System reset to factory defaults.")


@app.command()
def version():
    """Show version info."""
    print_success("Cortex v0.1.0")


@app.command()
def logs(tail: int = typer.Option(0, "--tail", help="Show last N log lines"),
         agent: str = typer.Option(None, "--agent", help="Show logs for specific agent")):
    """Show recent logs."""
    log_path = os.getenv("CORTEX_LOG_FILE", "./logs/cortex.log")
    if not os.path.exists(log_path):
        print_error(f"Log file not found at {log_path}")
        return
        
    with open(log_path, "r") as f:
        lines = f.readlines()
        if tail > 0:
            lines = lines[-tail:]
        for line in lines:
            if agent and agent not in line:
                continue
            console._print(line.strip()) # Output without Rich formatting to preserve original log format


# --- Agent commands ---
@agent_app.command("run")
def agent_run(name: str, task: str):
    """Run a task with a specific agent."""
    orch = get_orchestrator()
    try:
        asyncio.run(orch.run_agent_task(name, task))
    except Exception as e:
        print_error(f"Task execution failed: {str(e)}")


@agent_app.command("list")
def agent_list():
    """List all agents with status."""
    mem = get_memory()
    agents = mem.knowledge.list_agents()
    
    # Format for Rich Table directly from DB
    formatted = []
    for a in agents:
        formatted.append({
            "name": a["name"],
            "model": "Based on config",
            "skills": "Based on config"
        })
    print_agent_list(formatted)


# --- Workflow commands ---
@workflow_app.command("run")
def workflow_run(
    name: str,
    input_text: str = typer.Option(None, "--input", help="Run workflow with input context"),
):
    """Execute a workflow."""
    engine = get_workflow_engine()
    try:
        result = asyncio.run(engine.run(name, input_text))
        print_success("Workflow Output:")
        # Print outputs nicely
        for step, output in result["outputs"].items():
            print_info(f"\n--- Output of '{step}' ---\n{output}")
    except Exception as e:
        print_error(f"Workflow execution failed: {str(e)}")


@workflow_app.command("list")
def workflow_list():
    """List all available workflows."""
    workflows_path = os.getenv("CORTEX_WORKFLOWS_PATH", "./workflows")
    if not os.path.exists(workflows_path):
        print_error("Workflows directory not found.")
        return
        
    rows = []
    for f in os.listdir(workflows_path):
        if f.endswith(".yaml"):
            rows.append([f.replace(".yaml", ""), "Available"])
            
    print_generic_table("Workflows", ["Name", "Status"], rows)


# --- Memory commands ---
@memory_app.command("search")
def memory_search(query: str):
    """Semantic search across memory."""
    mem = get_memory()
    with show_spinner("Searching vector memory..."):
        results = mem.search(query, memory_type="company", top_k=5)
        
    if not results:
        print_info("No results found.")
        return
        
    for r in results:
        print_info(f"\n--- Match (Score: {r['distance']}) ---\n{r['content']}")


@memory_app.command("stats")
def memory_stats():
    """Storage usage stats."""
    mem = get_memory()
    stats = mem.get_stats()
    
    rows = [
        ["Total Size", f"{stats['total_storage_mb']} MB"],
        ["Limit", f"{stats['limit_gb']} GB"],
        ["Company Vectors", str(stats.get("company_memory_count", 0))],
        ["Department Vectors", str(stats.get("department_memory_count", 0))],
        ["Workflow Histories", str(stats.get("workflow_history_count", 0))],
        ["Agents Registered", str(stats.get("agents_count", 0))],
    ]
    print_generic_table("Memory Stats", ["Metric", "Value"], rows)


# --- Skill commands ---
@skill_app.command("list")
def skill_list():
    """List all available skills."""
    skills_path = "./skills"
    rows = []
    if os.path.exists(skills_path):
        for item in os.listdir(skills_path):
            if os.path.isdir(os.path.join(skills_path, item)) and not item.startswith("__"):
                rows.append([item, "1.0.0", "Installed"])
    print_generic_table("Skills", ["Name", "Version", "Status"], rows)


# --- Model commands ---
@model_app.command("list")
def model_list():
    """List all configured models."""
    router = get_router()
    avail = router.list_available()
    default = router.default_model
    
    rows = []
    for m in avail:
        is_def = "✓ Default" if m == default else ""
        provider = "OpenAI" if "gpt" in m else "Anthropic" if "claude" in m else "Groq/Ollama"
        rows.append([provider, m, is_def])
        
    print_generic_table("Models", ["Provider", "Model", "Default"], rows)
