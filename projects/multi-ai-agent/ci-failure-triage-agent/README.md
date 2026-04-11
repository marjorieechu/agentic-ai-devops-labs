# CI Failure Triage Agent

This project is a practical baseline for a DevOps-aligned agentic AI workflow.

It analyzes CI failure logs, classifies the likely issue, estimates severity, extracts key evidence, and suggests a next action. The current implementation is intentionally lightweight and local-first so the project is easy to run and extend.

## Why This Project

This is one of the strongest next projects for this repository because it connects AI work directly to engineering operations.

Instead of building another generic chatbot, this project focuses on a real workflow:

- a CI job fails
- logs need to be summarized quickly
- the likely root cause should be classified
- the next action should be suggested clearly

## Current Scope

The current version provides:

- a local CLI for analyzing CI logs
- heuristic classification for common failure patterns
- structured JSON output
- sample GitHub Actions-style log files
- unit tests for the core analysis behavior

## Planned Agentic Upgrades

The roadmap for this project is:

1. Add an LLM-based summarizer on top of the heuristic baseline
2. Connect to GitHub Actions logs through the GitHub API
3. Add issue drafting for failed workflows
4. Add RAG over historical failures and runbooks
5. Convert the workflow into a multi-step LangGraph or OpenAI Agents SDK system

## Project Structure

- `pyproject.toml` defines the Python project
- `src/ci_failure_triage_agent/` contains the analysis logic and CLI
- `samples/` contains example CI logs
- `tests/` contains unit tests

## Quick Start

```powershell
cd projects\ci-failure-triage-agent
$env:PYTHONPATH="src"
python -m ci_failure_triage_agent.cli --input samples\python_test_failure.log --pretty
```

## Example Output

```json
{
  "category": "test_failure",
  "severity": "medium",
  "confidence": "high",
  "summary": "The workflow failed because the test suite reported one or more failing tests.",
  "recommended_action": "Inspect the failing test names and the most recent code changes touching the affected module."
}
```

## Why This Is A Good Portfolio Project

It demonstrates:

- practical DevOps workflow understanding
- classification and structured output design
- a clean baseline before adding real agent orchestration
- a path toward memory, RAG, tool use, and multi-agent coordination

## Verification

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
```

## Next Step Recommendation

The best next upgrade is to add a second stage that uses an LLM to convert the structured triage result into:

- a GitHub issue draft
- a Slack-ready incident summary
- a suggested owner or investigation path
