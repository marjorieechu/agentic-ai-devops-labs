from __future__ import annotations

import argparse
import json
from pathlib import Path

from openai import APIError

from stateful_ai_agent.agent import StatefulAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a stateful AI agent using the OpenAI Agents SDK and SQLite session memory."
    )
    parser.add_argument(
        "--message",
        action="append",
        default=[],
        help="Message to send to the agent. Pass multiple times for a multi-turn session.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="OpenAI model to use. Defaults to OPENAI_MODEL or the project default.",
    )
    parser.add_argument(
        "--session-id",
        default="stateful_demo",
        help="Session identifier used by SQLiteSession.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("data/session.db"),
        help="Path to the SQLite database backing session memory.",
    )
    parser.add_argument(
        "--stateless",
        action="store_true",
        help="Disable SQLiteSession and run each turn without persisted conversation history.",
    )
    parser.add_argument(
        "--clear-session",
        action="store_true",
        help="Clear the existing SQLite session before sending messages.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.message:
        parser.error("Provide at least one --message value.")

    agent = StatefulAgent(
        model=args.model,
        session_id=args.session_id,
        db_path=args.db_path,
        stateless=args.stateless,
    )

    if args.clear_session:
        agent.clear_session()

    results = []
    try:
        for message in args.message:
            response = agent.respond(message)
            results.append(
                {
                    "message": message,
                    "response": response.to_dict(),
                }
            )
    except RuntimeError as exc:
        parser.exit(1, f"{exc}\n")
    except APIError as exc:
        parser.exit(1, f"OpenAI API error: {exc}\n")
    except Exception as exc:
        parser.exit(1, f"Unexpected error: {exc}\n")

    indent = 2 if args.pretty else None
    print(json.dumps(results, indent=indent))


if __name__ == "__main__":
    main()
