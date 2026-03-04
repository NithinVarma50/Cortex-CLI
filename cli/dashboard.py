import os
import sys
import webbrowser
from threading import Thread
from flask import Flask, render_template_string, jsonify, request
from memory.memory_manager import MemoryManager
from models.model_router import ModelRouter

app = Flask(__name__)

# Very basic inline HTML template to avoid needing a separate templates folder
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cortex OS - Dashboard</title>
    <style>
        :root {
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --primary: #38bdf8;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --success: #22c55e;
            --border: #334155;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            margin: 0;
            padding: 2rem;
            line-height: 1.5;
        }
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .logo span { color: var(--primary); }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .card {
            background-color: var(--bg-card);
            border-radius: 0.75rem;
            padding: 1.5rem;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        }
        .card h3 {
            margin-top: 0;
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            line-height: 1;
        }
        .stat-label {
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-top: 0.25rem;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: left;
            padding: 0.75rem 0;
            border-bottom: 1px solid var(--border);
        }
        th {
            color: var(--text-muted);
            font-weight: 500;
            font-size: 0.875rem;
        }
        .badge {
            background: #1e3a8a;
            color: #bfdbfe;
            padding: 0.25rem 0.5rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            display: inline-block;
            margin-right: 0.25rem;
            margin-bottom: 0.25rem;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
            color: var(--text-muted);
        }
        input, select {
            width: 100%;
            background: var(--bg-dark);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 0.5rem;
            border-radius: 0.375rem;
            box-sizing: border-box;
        }
        button {
            background-color: var(--primary);
            color: #0f172a;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        button:hover {
            opacity: 0.9;
        }
        .task-output {
            background: #0f172a;
            padding: 1rem;
            border-radius: 0.375rem;
            border: 1px solid var(--border);
            font-family: monospace;
            white-space: pre-wrap;
            min-height: 100px;
            margin-top: 1rem;
            color: #a7f3d0;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">🧠 Cortex <span>OS</span></div>
        <div style="color: var(--text-muted); font-size: 0.875rem;">Local Multi-Agent Platform</div>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Memory Status</h3>
            <div class="stat-value" id="memory-used">--</div>
            <div class="stat-label" id="memory-limit">of limit used</div>
            <div style="margin-top: 1rem; font-size: 0.875rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: var(--text-muted)">Total Vectors:</span>
                    <span id="vector-count">0</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>Configuration <button onclick="saveConfig()" style="font-size: 0.75rem; padding: 0.25rem 0.5rem;">Save</button></h3>
            <div class="form-group">
                <label>Default Model</label>
                <select id="default-model">
                    {% for p in models %}
                    <option value="{{ p }}" {% if p == default_model %}selected{% endif %}>{{ p }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label>OpenAI API Key <span style="font-size: 10px; color: var(--success);" id="key-status-msg"></span></label>
                <input type="password" id="openai-key" value="{{ openai_key }}" placeholder="sk-...">
            </div>
            <div class="form-group">
                <label>Anthropic API Key</label>
                <input type="password" id="anthropic-key" value="{{ anthropic_key }}" placeholder="sk-ant-...">
            </div>
        </div>
    </div>

    <div class="grid">
        <div class="card" style="grid-column: 1 / -1;">
            <h3>Agent Roster</h3>
            <table>
                <thead>
                    <tr>
                        <th>Agent Name</th>
                        <th>Role</th>
                        <th>Model</th>
                        <th>Assigned Skills</th>
                    </tr>
                </thead>
                <tbody>
                    {% for agent in agents %}
                    <tr>
                        <td style="font-weight: 500; color: var(--primary);">{{ agent.name }}</td>
                        <td style="color: var(--text-muted);">{{ agent.role }}</td>
                        <td>{{ agent.model or 'Default' }}</td>
                        <td>
                            {% set current_skills = agent.skills|fromjson if agent.skills else [] %}
                            {% for skill in current_skills %}
                                <span class="badge">{{ skill }}</span>
                            {% else %}
                                <span style="color: var(--text-muted); font-size: 0.875rem;">None</span>
                            {% endfor %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <div class="card">
        <h3>Run Agent Task</h3>
        <div class="form-group">
            <label>Select Agent</label>
            <select id="task-agent">
                {% for agent in agents %}
                <option value="{{ agent.name }}">{{ agent.name }} ({{ agent.role }})</option>
                {% endfor %}
            </select>
        </div>
        <div class="form-group">
            <label>Task Description</label>
            <input type="text" id="task-input" placeholder="E.g., Research recent LLM benchmarks...">
        </div>
        <button onclick="runTask()" id="run-btn">Execute Task</button>
        <div class="task-output" id="task-output">Ready.</div>
    </div>

    <script>
        // Load initial stats
        fetch('/api/stats')
            .then(r => r.json())
            .then(data => {
                document.getElementById('memory-used').innerText = `${data.total_storage_mb} MB`;
                document.getElementById('memory-limit').innerText = `of ${data.limit_gb} GB used`;
                document.getElementById('vector-count').innerText = data.company_memory_count + data.department_memory_count;
            });

        async function saveConfig() {
            const btn = document.querySelector('button[onclick="saveConfig()"]');
            btn.innerText = 'Saving...';
            
            const defaultModel = document.getElementById('default-model').value;
            const openAI = document.getElementById('openai-key').value;
            const anthropic = document.getElementById('anthropic-key').value;
            
            await fetch('/api/config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    CORTEX_DEFAULT_MODEL: defaultModel,
                    OPENAI_API_KEY: openAI,
                    ANTHROPIC_API_KEY: anthropic
                })
            });
            
            btn.innerText = 'Saved!';
            document.getElementById('key-status-msg').innerText = "Updated in .env";
            setTimeout(() => { btn.innerText = 'Save'; document.getElementById('key-status-msg').innerText = ""; }, 2000);
        }

        async function runTask() {
            const agent = document.getElementById('task-agent').value;
            const task = document.getElementById('task-input').value;
            if(!task) return;
            
            const btn = document.getElementById('run-btn');
            const output = document.getElementById('task-output');
            
            btn.innerText = 'Executing...';
            btn.disabled = true;
            output.innerText = `[Running] Sending task to ${agent}...\\n`;
            
            try {
                const response = await fetch('/api/run_task', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({agent, task})
                });
                
                const data = await response.json();
                if(data.error) {
                    output.innerText = `[Error]\\n` + data.error;
                } else {
                    output.innerText = data.result;
                }
            } catch(e) {
                output.innerText = `[Error] ${e.message}`;
            }
            
            btn.innerText = 'Execute Task';
            btn.disabled = false;
        }
    </script>
</body>
</html>
"""

@app.template_filter('fromjson')
def fromjson_filter(val):
    import json
    try:
        return json.loads(val)
    except:
        return []

@app.route("/")
def index():
    mem = MemoryManager()
    router = ModelRouter()
    
    agents = mem.knowledge.list_agents()
    models = router.list_available()
    
    return render_template_string(
        HTML_TEMPLATE, 
        agents=agents,
        models=models,
        default_model=router.default_model,
        openai_key=os.getenv("OPENAI_API_KEY", ""),
        anthropic_key=os.getenv("ANTHROPIC_API_KEY", "")
    )

@app.route("/api/stats")
def get_stats():
    return jsonify(MemoryManager().get_stats())

@app.route("/api/config", methods=["POST"])
def update_config():
    data = request.json
    env_path = ".env"
    
    # Simple .env updater
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
            
    for k, v in data.items():
        if not v: continue
        updated = False
        with open(env_path, "w") as f:
            for line in lines:
                if line.startswith(f"{k}="):
                    f.write(f"{k}={v}\n")
                    updated = True
                else:
                    f.write(line)
            if not updated:
                f.write(f"{k}={v}\n")
        # Update current env memory
        os.environ[k] = v
        # re-read for next key
        with open(env_path, "r") as f:
            lines = f.readlines()
            
    return jsonify({"status": "success"})


@app.route("/api/run_task", methods=["POST"])
def run_task():
    data = request.json
    from core.orchestrator import Orchestrator
    import asyncio
    
    orch = Orchestrator(MemoryManager(), ModelRouter())
    try:
        # In a real app we'd stream this via web sockets, but for simplicity we await
        result = asyncio.run(orch.run_agent_task(data["agent"], data["task"]))
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def start_dashboard(port=5742):
    """Launch the Flask app in a background thread and open browser."""
    print(f"\nStarting Cortex Control Panel on http://localhost:{port}")
    
    # Suppress flask startup messages
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    def run_server():
        app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)

    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Open browser automatically
    webbrowser.open(f"http://localhost:{port}")
    
    # Keep main thread alive IF we are running this as a standalone command
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
        sys.exit(0)
