from __future__ import annotations

import argparse
import json
from pathlib import Path

from langgraph_incident_command_graph.graph import DevOpsIncidentCommandGraph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the LangGraph DevOps incident command graph."
    )
    parser.add_argument("--prompt", required=False, help="Prompt to send to the graph.")
    parser.add_argument(
        "--model",
        default=None,
        help="OpenAI model to use. Defaults to OPENAI_MODEL or the project default.",
    )
    parser.add_argument(
        "--thread-id",
        default="default",
        help="LangGraph thread identifier for MemorySaver state.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    parser.add_argument(
        "--print-graph",
        action="store_true",
        help="Print the LangGraph structure as Mermaid text and exit.",
    )
    parser.add_argument(
        "--graph-output",
        type=Path,
        default=None,
        help="Write the LangGraph Mermaid text to a file.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        workflow = DevOpsIncidentCommandGraph(model=args.model)
        if args.print_graph or args.graph_output:
            mermaid = workflow.get_mermaid_graph()
            if args.graph_output:
                args.graph_output.write_text(mermaid, encoding="utf-8")
            if args.print_graph:
                print(mermaid)
            if not args.prompt:
                return
        if not args.prompt:
            parser.exit(2, "A --prompt is required unless you only want graph output.\n")
        result = workflow.run(args.prompt, thread_id=args.thread_id)
    except RuntimeError as exc:
        parser.exit(1, f"{exc}\n")
    except Exception as exc:
        parser.exit(1, f"Unexpected error: {exc}\n")

    print(json.dumps(result.to_dict(), indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
