from __future__ import annotations

from ci_failure_triage_agent.models import TriageResult


RULES = [
    {
        "category": "dependency_install_failure",
        "severity": "high",
        "confidence": "high",
        "summary": "The workflow failed during dependency installation or environment setup.",
        "recommended_action": "Check package registry availability, lockfile changes, dependency versions, and installation credentials.",
        "patterns": [
            "Could not find a version that satisfies the requirement",
            "No matching distribution found",
            "npm ERR!",
            "poetry install",
            "pip install",
            "ResolutionImpossible",
        ],
    },
    {
        "category": "test_failure",
        "severity": "medium",
        "confidence": "high",
        "summary": "The workflow failed because the test suite reported one or more failing tests.",
        "recommended_action": "Inspect the failing test names and the most recent code changes touching the affected module.",
        "patterns": [
            "FAILED ",
            "AssertionError",
            "Test suite failed to run",
            "E       AssertionError",
        ],
    },
    {
        "category": "lint_or_format_failure",
        "severity": "low",
        "confidence": "high",
        "summary": "The workflow failed on linting, formatting, or static quality checks.",
        "recommended_action": "Run the local formatter or linter, inspect the reported file paths, and push the resulting fixes.",
        "patterns": [
            "black --check",
            "would reformat",
            "eslint",
            "prettier",
            "ruff",
            "flake8",
            "isort",
        ],
    },
    {
        "category": "build_failure",
        "severity": "high",
        "confidence": "medium",
        "summary": "The workflow failed while compiling, packaging, or building the application.",
        "recommended_action": "Review the build step output, check recent configuration changes, and reproduce the build locally.",
        "patterns": [
            "Build failed",
            "Compilation failed",
            "Module not found",
            "Cannot find module",
            "error TS",
            "webpack",
        ],
    },
    {
        "category": "authentication_or_secret_failure",
        "severity": "high",
        "confidence": "high",
        "summary": "The workflow could not access a protected resource because of missing or invalid credentials.",
        "recommended_action": "Verify repository secrets, token scopes, service credentials, and environment variable injection.",
        "patterns": [
            "401",
            "403",
            "unauthorized",
            "forbidden",
            "permission denied",
            "authentication failed",
            "access denied",
        ],
    },
]


def analyze_log(log_text: str) -> TriageResult:
    lines = [line.rstrip() for line in log_text.splitlines()]
    normalized = log_text.lower()

    best_rule = None
    best_matches: list[str] = []

    for rule in RULES:
        matched_patterns = [
            pattern
            for pattern in rule["patterns"]
            if pattern.lower() in normalized
        ]
        if len(matched_patterns) > len(best_matches):
            best_rule = rule
            best_matches = matched_patterns

    if best_rule is None or not best_matches:
        return TriageResult(
            category="unknown_failure",
            severity="medium",
            confidence="low",
            summary="The workflow failed, but the current baseline classifier could not confidently identify the failure type.",
            recommended_action="Review the final error lines, capture a representative sample, and extend the classifier or add an LLM-based analysis step.",
            evidence=_collect_evidence(lines, []),
        )

    return TriageResult(
        category=best_rule["category"],
        severity=best_rule["severity"],
        confidence=best_rule["confidence"],
        summary=best_rule["summary"],
        recommended_action=best_rule["recommended_action"],
        evidence=_collect_evidence(lines, best_matches),
    )


def _collect_evidence(lines: list[str], patterns: list[str], limit: int = 5) -> list[str]:
    evidence: list[str] = []
    lowered_patterns = [pattern.lower() for pattern in patterns]

    for line in lines:
        candidate = line.strip()
        if not candidate:
            continue
        if lowered_patterns and any(pattern in candidate.lower() for pattern in lowered_patterns):
            evidence.append(candidate)
        elif not lowered_patterns and _looks_like_failure_signal(candidate):
            evidence.append(candidate)

        if len(evidence) >= limit:
            break

    if evidence:
        return evidence

    tail = [line.strip() for line in lines if line.strip()]
    return tail[-limit:]


def _looks_like_failure_signal(line: str) -> bool:
    lowered = line.lower()
    return any(
        token in lowered
        for token in ("error", "failed", "failure", "traceback", "exception")
    )
