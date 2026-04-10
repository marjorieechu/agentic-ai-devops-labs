from __future__ import annotations

import argparse
import json
from pathlib import Path

from ci_failure_triage_agent.analyzer import analyze_log


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze CI failure logs and return a structured triage result."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to a CI log file.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    log_text = args.input.read_text(encoding="utf-8")
    result = analyze_log(log_text)
    indent = 2 if args.pretty else None
    print(json.dumps(result.to_dict(), indent=indent))


if __name__ == "__main__":
    main()
