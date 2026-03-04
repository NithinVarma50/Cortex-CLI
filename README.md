# 🧠 Cortex — AI Operating System

> Local-first multi-agent AI platform for companies and developers.

## Install

pip install cortex-ai

## Quick Start

cortex init
cortex agent run research_agent "Research the EV market in 2025"

## Commands
* `cortex init` — Initialize Cortex in current directory
* `cortex start` — Start the Cortex daemon / interactive shell
* `cortex status` — Show system status
* `cortex agent list` — List all agents
* `cortex workflow run <name>` — Execute a workflow

## Agents
Cortex comes with pre-built agents like `finance_agent`, `marketing_agent`, `operations_agent`, `legal_agent`, and `research_agent`.

## Workflows
Run complex sequence of autonomous agent tasks using standard YAML definitions.

## Configuration
Configure Cortex with `cortex config set <key> <value>` or edit `~/.cortex/cortex.yaml`.
