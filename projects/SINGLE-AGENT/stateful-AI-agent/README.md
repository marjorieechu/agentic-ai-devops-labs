# Stateful AI Agent

This project represents a memory-enabled AI agent.

It is the stateful counterpart to a stateless agent: instead of treating every prompt as an isolated request, it keeps conversation history so follow-up questions can use prior context. It does not use tools in the current version; the LLM and session history are the main sources of behavior.

The current implementation uses the OpenAI Agents SDK directly with `Agent`, `Runner.run_sync(...)`, and `SQLiteSession(...)`, and it is now specialized as a memory-enabled market research assistant with structured JSON output.

- first, an agent is run with no memory
- then a follow-up question fails because earlier context is missing
- finally, memory is added with `SQLiteSession`
- the same follow-up now works because the agent can access prior conversation state

That pattern is the core idea behind this project.

## What "Stateful" Means Here

In this repository, a stateful AI agent is an agent that can retain or retrieve prior interaction data across steps in a workflow or across user turns.

For this project, statefulness mainly means:

- preserving conversation history
- using stored context in later responses
- avoiding loss of meaning in follow-up questions
- creating a better user experience for multi-turn tasks

Relevant material:

- `1. Build a Simple AI Agent With OpenAI Agents SDK.ipynb`
- `2. AI Agents with Memory.ipynb`
- `3. AI Agents with Tools.ipynb`

The memory notebook specifically demonstrates:

- creating an agent with the OpenAI Agents SDK
- running it once without memory
- asking a follow-up question that depends on earlier context
- adding `SQLiteSession("conversation")`
- rerunning the interaction so the agent remembers the earlier exchange

One example from the notebook uses a market research assistant and asks:

- `What is the market share of Tesla in the US EV market?`
- `How does that compare to last year?`

Without memory, the second question lacks context. With `SQLiteSession`, the agent can interpret the follow-up correctly.

## Intended Scope

This project is meant to be a practical baseline for building memory-aware agent behavior before moving into more advanced orchestration.

The likely implementation scope is:

- a single agent with clear instructions
- persistent session storage
- multi-turn interaction support
- a small CLI, notebook, or script entry point
- examples showing the difference between stateless and stateful behavior

## Suggested Stack

- Python
- OpenAI Agents SDK
- `SQLiteSession` for local persistent memory
- `python-dotenv` for environment loading

## Current Project Structure

- `pyproject.toml` defines the Python project and dependencies
- `src/stateful_ai_agent/agent.py` contains the OpenAI Agents SDK wrapper
- `src/stateful_ai_agent/cli.py` provides the runnable CLI
- `tests/test_agent.py` contains mocked tests for session behavior
- `data/session.db` stores local SQLite session memory

## Progress So Far

The project has moved through these concrete steps:

1. Started as a stateful-agent concept based on the course notebook `2. AI Agents with Memory.ipynb`
2. Added a local README describing what memory means in a single-agent workflow
3. Scaffolded a runnable Python project with CLI and tests
4. Migrated the implementation to the real OpenAI Agents SDK using `Agent`, `Runner.run_sync(...)`, and `SQLiteSession(...)`
5. Added `.env` support for local development and protected secrets with repo-level `.gitignore` rules
6. Added `.env.example` so setup can be reproduced safely without exposing real credentials
7. Verified that `.env` is ignored by Git and therefore should not be pushed
8. Converted the agent from a generic assistant into a market research assistant
9. Added structured output with fields for `subject`, `verdict`, `summary`, and `memory_note`
10. Updated tests to mock the SDK cleanly and keep the suite stable in local development
11. Corrected shell-specific run instructions so both PowerShell and Git Bash usage are documented

## Current Status

What is working now:

- OpenAI Agents SDK integration is in place
- SQLite session memory is wired into the agent
- structured JSON output is implemented
- local tests pass
- Git-safe secret handling is documented

What still depends on your local environment:

- live API runs depend on the configured `OPENAI_API_KEY`
- the selected `OPENAI_MODEL` must exist for your account
- CLI commands must match the shell you are using, especially for `PYTHONPATH`

## Setup

Set your OpenAI API key before running the CLI:

PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

Optional model override:

PowerShell:

```powershell
$env:OPENAI_MODEL="gpt-5.4-mini"
```

Git Bash:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-5.4-mini"
```

Install dependencies from this project folder:

```powershell
cd projects\SINGLE-AGENT\stateful-AI-agent
pip install -e .
```

Git Bash:

```bash
cd projects/SINGLE-AGENT/stateful-AI-agent
pip install -e .
```

## Quick Start

Run a stateful multi-turn conversation:

PowerShell:

```powershell
cd projects\SINGLE-AGENT\stateful-AI-agent
$env:PYTHONPATH="src"
python -m stateful_ai_agent.cli --clear-session --session-id tesla-demo --message "What is the market share of Tesla in the US EV market?" --message "How does that compare to last year?" --pretty
```

Git Bash:

```bash
cd projects/SINGLE-AGENT/stateful-AI-agent
PYTHONPATH=src python -m stateful_ai_agent.cli --clear-session --session-id tesla-demo --message "What is the market share of Tesla in the US EV market?" --message "How does that compare to last year?" --pretty
```

Run the same conversation without memory:

PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m stateful_ai_agent.cli --stateless --message "What is the market share of Tesla in the US EV market?" --message "How does that compare to last year?" --pretty
```

Git Bash:

```bash
PYTHONPATH=src python -m stateful_ai_agent.cli --stateless --message "What is the market share of Tesla in the US EV market?" --message "How does that compare to last year?" --pretty
```

Reuse the same session later:

PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m stateful_ai_agent.cli --session-id tesla-demo --message "Tell me more about that trend." --pretty
```

Git Bash:

```bash
PYTHONPATH=src python -m stateful_ai_agent.cli --session-id tesla-demo --message "Tell me more about that trend." --pretty
```

Use a different model explicitly:

PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m stateful_ai_agent.cli --model gpt-5.4-mini --message "Summarize our last topic." --pretty
```

Git Bash:

```bash
PYTHONPATH=src python -m stateful_ai_agent.cli --model gpt-5.4-mini --message "Summarize our last topic." --pretty
```

Minimal smoke test:

PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m stateful_ai_agent.cli --clear-session --session-id smoke-test --message "Reply briefly: what company are we discussing if I say Tesla?" --pretty
```

Git Bash:

```bash
PYTHONPATH=src python -m stateful_ai_agent.cli --clear-session --session-id smoke-test --message "Reply briefly: what company are we discussing if I say Tesla?" --pretty
```

Example response shape:

```json
[
  {
    "message": "How does that compare to last year?",
    "response": {
      "answer": {
        "subject": "Tesla",
        "verdict": "FACT",
        "summary": "Tesla is the active subject carried forward from the prior turn.",
        "memory_note": "The session history allowed the agent to resolve 'that' to Tesla."
      },
      "model": "gpt-5.4-mini",
      "session_enabled": true,
      "session_id": "tesla-demo",
      "history_items": 4
    }
  }
]
```

## Sample Output

A successful local run has been captured here:

[memory-based-response.png](/C:/Users/user/Documents/AGENTIC-AI/AgenticAI-GenerativeAI-projects/projects/SINGLE-AGENT/stateful-AI-agent/memory-based-response.png)

The screenshot shows:

- execution from Git Bash using `PYTHONPATH=src`
- a successful OpenAI response using `gpt-5.4-mini`
- structured output with `subject`, `verdict`, `summary`, and `memory_note`
- session-backed memory metadata including `session_enabled`, `session_id`, and `history_items`

## Test

Run the local test suite:

PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
```

Git Bash:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Troubleshooting

- If you are using Git Bash, do not use PowerShell syntax like `$env:PYTHONPATH="src"`. Use `PYTHONPATH=src python -m ...` or `export PYTHONPATH=src`.
- If `stateful_ai_agent` cannot be imported, either set `PYTHONPATH=src` for the command or install the project with `pip install -e .`.
- If the CLI returns an OpenAI model error, check your `.env` and confirm `OPENAI_MODEL` matches a model available to your account.
- If a live run works on your machine but not in a restricted sandbox, the issue is usually outbound network access rather than the project code.

## Example Use Cases

- market research follow-up questions
- travel planning that remembers prior destinations
- support assistants that retain issue context
- study assistants that remember the current topic

## What This Project Proves

- memory changes agent behavior in a visible way
- state can be preserved across interactions
- follow-up questions become more useful and coherent
- the project can serve as a stepping stone toward richer agent systems with tools, retrieval, and orchestration

## Recommended Next Steps

1. Add tools or retrieval so market data answers can be grounded instead of model-only
2. Add evaluation cases for ambiguous follow-up questions across multiple turns
3. Introduce a company-comparison mode for competitor analysis
4. Add source citation fields once retrieval is enabled
5. Introduce handoffs later if this grows into a multi-agent workflow
