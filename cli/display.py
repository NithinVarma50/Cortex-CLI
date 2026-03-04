import sys
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

# Global console instance
console = Console()

# Theme Colors
PRIMARY = "bold cyan"
SUCCESS = "bold green"
WARNING = "bold yellow"
ERROR = "bold red"
INFO = "dim white"
ACCENT = "bold magenta"


def print_banner(version: str = "0.1.0"):
    """Display the Cortex startup banner."""
    banner_text = Text(
        f"  🧠 CORTEX v{version} — AI Operating System ", style=PRIMARY
    )
    console.print(
        Panel(
            banner_text,
            expand=False,
            style=PRIMARY,
            border_style=PRIMARY,
        )
    )


def print_status(
    agents_count: int, memory_used_mb: int, memory_limit_gb: int, default_model: str
):
    """Display system status panel."""
    console.print(f"[{SUCCESS}]✓[/{SUCCESS}] Loaded {agents_count} agents")
    console.print(
        f"[{SUCCESS}]✓[/{SUCCESS}] Memory: {memory_used_mb}MB / {memory_limit_gb}GB used"
    )
    console.print(f"[{SUCCESS}]✓[/{SUCCESS}] Default model: {default_model}")
    console.print()
    console.print("Run 'cortex --help' to see all commands.", style=INFO)


def print_success(message: str):
    console.print(f"[{SUCCESS}]✓ {message}[/{SUCCESS}]")


def print_error(message: str):
    console.print(f"[{ERROR}]✗ {message}[/{ERROR}]", file=sys.stderr)


def print_warning(message: str):
    console.print(f"[{WARNING}]! {message}[/{WARNING}]")


def print_info(message: str):
    console.print(f"[{INFO}]{message}[/{INFO}]")


def print_agent_list(agents_data: List[Dict[str, str]]):
    """Print a table of agents."""
    table = Table(show_header=True, header_style=PRIMARY, border_style=INFO)
    table.add_column("Agent")
    table.add_column("Model")
    table.add_column("Skills")

    for agent in agents_data:
        table.add_row(
            agent.get("name", "Unknown"),
            agent.get("model", "Unknown"),
            agent.get("skills", "None"),
        )
    console.print(table)


def print_generic_table(
    title: str, headers: List[str], rows: List[List[str]], style: str = PRIMARY
):
    table = Table(
        title=title, show_header=True, header_style=style, border_style=INFO
    )
    for h in headers:
        table.add_column(h)
    for r in rows:
        table.add_row(*r)
    console.print(table)


@contextmanager
def show_spinner(text: str = "Processing..."):
    """Context manager for showing a spinner during an operation."""
    with Progress(
        SpinnerColumn(style=ACCENT),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description=text, total=None)
        yield
