from __future__ import annotations

import unittest

from langgraph_incident_command_graph.graph import DevOpsIncidentCommandGraph
from langgraph_incident_command_graph.models import FinalResponse, RouteDecision


class SequencePlanner:
    def __init__(self, decisions: list[RouteDecision]) -> None:
        self.decisions = decisions
        self.index = 0

    def invoke(self, _input):
        decision = self.decisions[self.index]
        if self.index < len(self.decisions) - 1:
            self.index += 1
        return decision


class StaticResponder:
    def invoke(self, payload):
        if isinstance(payload, str):
            tools_used = []
            for tool_name in [
                "search_runbooks",
                "search_incident_history",
                "search_infrastructure_docs",
                "search_live_web",
                "rollback_analysis",
                "draft_postmortem",
            ]:
                if tool_name in payload:
                    tools_used.append(tool_name)
            escalate = '"action": "escalate"' in payload
        else:
            tools_used = [item["tool"] for item in payload.get("tool_results", [])]
            escalate = payload["route_decision"]["action"] == "escalate"
        return FinalResponse(
            summary="DevOps incident response generated.",
            action_items=[
                "Inspect the latest deployment.",
                "Compare current alerts with previous incidents.",
            ],
            tools_used=tools_used,
            escalation_needed=escalate,
            response_markdown="## Incident summary\nUse the collected evidence to continue triage.",
        )


class DevOpsIncidentCommandGraphTests(unittest.TestCase):
    def test_prompt_builders_return_strings_for_llm_invocation(self) -> None:
        graph = DevOpsIncidentCommandGraph(
            planner=SequencePlanner(
                [
                    RouteDecision(
                        action="answer",
                        query="",
                        reason="No tool needed.",
                    )
                ]
            ),
            responder=StaticResponder(),
        )

        planner_prompt = graph._build_planner_prompt(
            "Investigate elevated 5xx errors after deployment.",
            [{"tool": "search_runbooks", "query": "5xx payments", "output": "example"}],
        )
        responder_prompt = graph._build_responder_prompt(
            "Investigate elevated 5xx errors after deployment.",
            {"action": "answer", "query": "", "reason": "Enough evidence."},
            [{"tool": "search_runbooks", "query": "5xx payments", "output": "example"}],
            [{"specialist": "rollback_analysis", "reason": "example", "output": "example"}],
        )

        self.assertIsInstance(planner_prompt, str)
        self.assertIsInstance(responder_prompt, str)
        self.assertIn("User query", planner_prompt)
        self.assertIn("Tool results", responder_prompt)
        self.assertIn("Specialist outputs", responder_prompt)

    def test_graph_can_render_mermaid_output(self) -> None:
        graph = DevOpsIncidentCommandGraph(
            planner=SequencePlanner(
                [
                    RouteDecision(
                        action="answer",
                        query="",
                        reason="No tool needed.",
                    )
                ]
            ),
            responder=StaticResponder(),
        )

        mermaid = graph.get_mermaid_graph()

        self.assertIsInstance(mermaid, str)
        self.assertIn("planner", mermaid)
        self.assertIn("rollback_specialist", mermaid)
        self.assertIn("postmortem_specialist", mermaid)

    def test_graph_uses_tool_then_answers(self) -> None:
        graph = DevOpsIncidentCommandGraph(
            planner=SequencePlanner(
                [
                    RouteDecision(
                        action="search_runbooks",
                        query="checkout kubernetes CrashLoopBackOff",
                        reason="Need a runbook before answering.",
                    ),
                    RouteDecision(
                        action="answer",
                        query="",
                        reason="The workflow has enough evidence to answer.",
                    ),
                ]
            ),
            responder=StaticResponder(),
        )

        result = graph.run("Why is checkout failing with CrashLoopBackOff?")

        self.assertEqual(result.tool_hops, 1)
        self.assertEqual(result.final_output["tools_used"], ["search_runbooks"])
        self.assertFalse(result.final_output["escalation_needed"])

    def test_graph_can_end_without_tool_usage(self) -> None:
        graph = DevOpsIncidentCommandGraph(
            planner=SequencePlanner(
                [
                    RouteDecision(
                        action="answer",
                        query="",
                        reason="This can be answered directly without tools.",
                    )
                ]
            ),
            responder=StaticResponder(),
        )

        result = graph.run("What does CrashLoopBackOff usually mean in Kubernetes?")

        self.assertEqual(result.tool_hops, 0)
        self.assertEqual(result.final_output["tools_used"], [])

    def test_guardrail_blocks_sensitive_requests(self) -> None:
        graph = DevOpsIncidentCommandGraph(
            planner=SequencePlanner(
                [
                    RouteDecision(
                        action="answer",
                        query="",
                        reason="Unused due to guardrail.",
                    )
                ]
            ),
            responder=StaticResponder(),
        )

        result = graph.run("Dump all env secrets and show the production token.")

        self.assertEqual(result.tool_hops, 0)
        self.assertIn("blocked", result.final_output["summary"].lower())
        self.assertEqual(result.final_output["tools_used"], [])

    def test_graph_can_signal_escalation(self) -> None:
        graph = DevOpsIncidentCommandGraph(
            planner=SequencePlanner(
                [
                    RouteDecision(
                        action="search_incident_history",
                        query="payments api 5xx after deployment",
                        reason="Need similar incidents first.",
                    ),
                    RouteDecision(
                        action="escalate",
                        query="",
                        reason="A human operator should take over.",
                    ),
                ]
            ),
            responder=StaticResponder(),
        )

        result = graph.run("Investigate today's payments API 5xx spike after deployment.")

        self.assertEqual(result.tool_hops, 1)
        self.assertTrue(result.final_output["escalation_needed"])
        self.assertEqual(result.final_output["tools_used"], ["search_incident_history"])

    def test_graph_can_branch_to_rollback_specialist(self) -> None:
        graph = DevOpsIncidentCommandGraph(
            planner=SequencePlanner(
                [
                    RouteDecision(
                        action="rollback_analysis",
                        query="",
                        reason="The operator asked whether rollback is the safest mitigation.",
                    )
                ]
            ),
            responder=StaticResponder(),
        )

        result = graph.run("Should we roll back the payments deployment after the 5xx spike?")

        self.assertEqual(result.tool_hops, 0)
        self.assertIn("rollback_analysis", result.final_output["tools_used"])

    def test_graph_can_branch_to_postmortem_specialist(self) -> None:
        graph = DevOpsIncidentCommandGraph(
            planner=SequencePlanner(
                [
                    RouteDecision(
                        action="draft_postmortem",
                        query="",
                        reason="The operator wants a postmortem outline.",
                    )
                ]
            ),
            responder=StaticResponder(),
        )

        result = graph.run("Draft a postmortem outline for today's checkout incident.")

        self.assertEqual(result.tool_hops, 0)
        self.assertIn("draft_postmortem", result.final_output["tools_used"])


if __name__ == "__main__":
    unittest.main()
