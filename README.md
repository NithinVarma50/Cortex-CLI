# 🧠 Cortex — AI Operating System

> Local-first multi-agent AI platform for companies and developers.
> Build AI departments that collaborate through shared memory, workflows, and skills — all running on your machine.

---

## ⚡ Quick Install

### Option 1: Install directly from GitHub (recommended)
```bash
pip install git+https://github.com/NithinVarma50/Cortex-CLI.git
```

### Option 2: Clone and install locally
```bash
git clone https://github.com/NithinVarma50/Cortex-CLI.git
cd Cortex-CLI
pip install -r requirements.txt
pip install -e .
```

### Verify installation
```bash
cortex version
```

---

## 🚀 Getting Started

### 1. Initialize Cortex
```bash
cortex init
```
This creates `storage/`, `logs/`, `config/` folders, sets up SQLite + ChromaDB, and registers default agents.

### 2. Add your API keys
Edit the `.env` file created in your project root:
```env
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=your-key-here
GROQ_API_KEY=your-key-here
```
> 💡 For local-only usage with **Ollama**, no API keys are needed. Just install [Ollama](https://ollama.com) and pull a model like `ollama pull llama3`.

### 3. Run your first task
```bash
cortex agent run research_agent "Research the EV market in 2025"
```

---

## 📋 All Commands

### System
| Command | Description |
|---------|-------------|
| `cortex init` | Initialize Cortex, create storage & config |
| `cortex start` | Start the Cortex interactive shell |
| `cortex status` | Show system status: agents, memory, workflows |
| `cortex version` | Show version info |
| `cortex reset --confirm` | Reset all memory and agents |
| `cortex logs` | Show recent logs |
| `cortex logs --tail 50` | Show last 50 log lines |
| `cortex logs --agent finance_agent` | Show logs for a specific agent |

### Configuration
| Command | Description |
|---------|-------------|
| `cortex config set <key> <value>` | Set a global config value |
| `cortex config show` | Display all configuration |

### Agents
| Command | Description |
|---------|-------------|
| `cortex agent list` | List all agents with status |
| `cortex agent run <name> "<task>"` | Run a task with a specific agent |
| `cortex agent create <name> --role <role> --model <model>` | Create a new agent |
| `cortex agent delete <name>` | Remove an agent |
| `cortex agent info <name>` | Show agent details, skills, memory |
| `cortex agent assign-skill <agent> <skill>` | Assign a skill to an agent |
| `cortex agent set-model <agent> <model>` | Change agent's LLM model |

### Workflows
| Command | Description |
|---------|-------------|
| `cortex workflow list` | List all available workflows |
| `cortex workflow run <name>` | Execute a workflow |
| `cortex workflow run <name> --input "<text>"` | Run workflow with input context |
| `cortex workflow create <name>` | Scaffold a new workflow YAML |
| `cortex workflow history` | Show past workflow runs |
| `cortex workflow status <run_id>` | Check status of a running workflow |

### Memory
| Command | Description |
|---------|-------------|
| `cortex memory show` | Display stored memory summary |
| `cortex memory search "<query>"` | Semantic search across all memory |
| `cortex memory add "<text>" --type <type>` | Manually add to memory |
| `cortex memory stats` | Show storage usage stats |
| `cortex memory clear --confirm` | Wipe all memory |
| `cortex memory export <filepath>` | Export memory to JSON |

### Skills
| Command | Description |
|---------|-------------|
| `cortex skill list` | List all available skills |
| `cortex skill install <name>` | Install a skill |
| `cortex skill uninstall <name>` | Remove a skill |
| `cortex skill info <name>` | Show skill description + usage |

### Models
| Command | Description |
|---------|-------------|
| `cortex model list` | List all configured models |
| `cortex model add <provider> --api-key <key>` | Add a model provider |
| `cortex model test <model_name>` | Test model connection |
| `cortex model set-default <model_name>` | Set default model |

---

## 🤖 Built-in Agents

| Agent | Role | Default Model | Skills |
|-------|------|---------------|--------|
| `finance_agent` | Senior Financial Analyst | gpt-4o | spreadsheet_analyzer, file_reader |
| `marketing_agent` | Marketing Strategist | claude-3-5-sonnet | web_search, file_reader |
| `operations_agent` | Operations Manager | gpt-4o | file_reader, code_executor |
| `legal_agent` | Legal Advisor | gpt-4o | file_reader, web_search |
| `research_agent` | Research Specialist | llama3-70b | web_search, file_reader |

---

## ⚡ Workflows

Cortex supports YAML-defined multi-agent workflows with dependency resolution. Three built-in workflows are included:

- **`product_launch`** — Research → Marketing → Finance → Operations
- **`marketing_campaign`** — Research → Draft Copy → Legal Review → Finalize
- **`financial_analysis`** — Data Gathering → Market Context → Analysis → Audit

### Run a workflow:
```bash
cortex workflow run product_launch --input "Electric SUV for Gen Z"
```

---

## 🧠 Memory System

Cortex uses a 3-layer hybrid memory:

1. **Vector Memory** (ChromaDB) — Semantic search across all knowledge
2. **Structured Memory** (SQLite) — Fast lookup for agents, tasks, events
3. **Working Memory** (In-process) — Active session context

Every agent output is automatically saved for future context retrieval.

---

## 🔌 Supported LLM Providers

| Provider | Models | Auth |
|----------|--------|------|
| OpenAI | gpt-4o, gpt-4-turbo, gpt-3.5-turbo | `OPENAI_API_KEY` |
| Anthropic | claude-3-5-sonnet, claude-3-haiku | `ANTHROPIC_API_KEY` |
| Groq | llama3-70b, mixtral-8x7b | `GROQ_API_KEY` |
| Ollama | llama3, mistral, gemma, deepseek | Local (no key) |

---

## 📁 Project Structure

```
cortex/
├── cli/           # Typer CLI + Rich terminal UI
├── core/          # Orchestrator, task router, workflow engine
├── agents/        # Base agent + 5 specialized agents
├── memory/        # Vector store, knowledge store, history
├── models/        # LLM provider integrations
├── skills/        # Plugin skills (web search, file reader, etc.)
├── tools/         # Filesystem, browser, shell tools
├── workflows/     # YAML workflow definitions
├── config/        # Agent, skill, model configuration
└── tests/         # Pytest test suites
```

---

## 🛡️ Security

- API keys stored only in `.env` (never logged or hardcoded)
- Code executor runs Python in a sandboxed subprocess (no shell access)
- File reader restricted to safe file types
- Memory isolation between agent departments

---

## 📄 License

MIT License — Built by [Nithin Varma](https://github.com/NithinVarma50)
