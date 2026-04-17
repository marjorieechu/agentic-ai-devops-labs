from __future__ import annotations

import os
from typing import Callable

import requests


RUNBOOKS = [
    {
        "title": "Kubernetes CrashLoopBackOff Runbook",
        "keywords": ["kubernetes", "crashloopbackoff", "pod", "restart", "deployment"],
        "content": (
            "Inspect pod events, confirm image and env vars, review readiness and liveness "
            "probes, and compare the failing rollout with the previous ReplicaSet."
        ),
    },
    {
        "title": "High 5xx API Error Runbook",
        "keywords": ["5xx", "api", "gateway", "latency", "payments", "checkout"],
        "content": (
            "Check upstream dependency saturation, recent deploys, ingress error rates, and "
            "database connection pool pressure before rolling back."
        ),
    },
    {
        "title": "CI Pipeline Failure Triage",
        "keywords": ["ci", "pipeline", "build", "test", "deploy", "artifact"],
        "content": (
            "Validate the failed stage, compare the last passing run, inspect secret injection, "
            "and confirm the target artifact still exists."
        ),
    },
]

INCIDENT_HISTORY = [
    {
        "title": "2026-04-14 Payments API 5xx Spike",
        "keywords": ["payments", "5xx", "database", "connection", "timeout"],
        "content": (
            "A mis-sized connection pool after deployment caused elevated 5xx errors until the "
            "pool limit and pod concurrency settings were corrected."
        ),
    },
    {
        "title": "2026-04-09 Checkout CrashLoopBackOff",
        "keywords": ["checkout", "crashloopbackoff", "secret", "configmap", "pod"],
        "content": (
            "Pods failed during startup because a required secret reference changed names during "
            "a Helm values update."
        ),
    },
    {
        "title": "2026-03-28 CI Release Blocker",
        "keywords": ["ci", "release", "pipeline", "artifact", "registry"],
        "content": (
            "Publishing failed because the registry token expired, which blocked image pushes and "
            "downstream deployment jobs."
        ),
    },
]

INFRA_DOCS = [
    {
        "title": "Payments Service Architecture",
        "keywords": ["payments", "service", "api", "database", "redis", "deployment"],
        "content": (
            "The payments API depends on PostgreSQL, Redis, and the internal risk-check service. "
            "Rolling updates are configured with maxUnavailable=0 and maxSurge=1."
        ),
    },
    {
        "title": "Cluster Operations Guide",
        "keywords": ["kubernetes", "cluster", "node", "pod", "probe", "deployment"],
        "content": (
            "Critical services require passing readiness checks before traffic shifts. Probe "
            "misconfiguration can produce restart loops and false-positive health states."
        ),
    },
    {
        "title": "Observability Query Guide",
        "keywords": ["latency", "alerts", "dashboard", "logs", "metrics", "5xx"],
        "content": (
            "Use error-rate dashboards first, then compare logs and deploy markers across the last "
            "two releases to isolate regressions."
        ),
    },
]


def _score_match(query: str, entry: dict[str, object]) -> int:
    tokens = {token.strip(".,:;!?").lower() for token in query.split()}
    keywords = set(entry["keywords"])
    return len(tokens & keywords)


def _search_fixture_store(query: str, entries: list[dict[str, object]], source: str) -> str:
    ranked = sorted(entries, key=lambda item: _score_match(query, item), reverse=True)
    matches = [item for item in ranked if _score_match(query, item) > 0][:2]
    if not matches:
        matches = ranked[:1]
    lines = [f"Source: {source}"]
    for item in matches:
        lines.append(f"- {item['title']}: {item['content']}")
    return "\n".join(lines)


def search_runbooks(query: str) -> str:
    return _search_fixture_store(query, RUNBOOKS, "runbooks")


def search_incident_history(query: str) -> str:
    return _search_fixture_store(query, INCIDENT_HISTORY, "incident_history")


def search_infrastructure_docs(query: str) -> str:
    return _search_fixture_store(query, INFRA_DOCS, "infrastructure_docs")


def search_live_web(query: str, *, max_results: int = 3) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Source: live_web\n- TAVILY_API_KEY is not configured, so live web search was skipped."

    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
        },
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code != 200:
        return f"Source: live_web\n- Tavily API error: {response.status_code}"

    results = response.json().get("results", [])
    if not results:
        return "Source: live_web\n- No relevant live web results found."

    lines = ["Source: live_web"]
    for item in results[:max_results]:
        lines.append(f"- {item['title']}: {item['content']}")
    return "\n".join(lines)


TOOL_REGISTRY: dict[str, Callable[[str], str]] = {
    "search_runbooks": search_runbooks,
    "search_incident_history": search_incident_history,
    "search_infrastructure_docs": search_infrastructure_docs,
    "search_live_web": search_live_web,
}
