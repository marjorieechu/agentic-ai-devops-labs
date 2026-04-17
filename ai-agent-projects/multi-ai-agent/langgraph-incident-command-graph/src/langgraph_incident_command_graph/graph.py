from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Protocol, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from langgraph_incident_command_graph.models import FinalResponse, RouteDecision, WorkflowRunResult
from langgraph_incident_command_graph.tools import TOOL_REGISTRY


DEFAULT_MODEL = "gpt-5.4-mini"
DEFAULT_WORKFLOW_NAME = "LangGraph Incident Command Graph"
MAX_TOOL_HOPS = 3


class Invokable(Protocol):
    def invoke(self, input: Any) -> Any:
        ...


class DevOpsAgentState(TypedDict, total=False):
    user_query: str
    route: dict[str, Any]
    tool_results: list[dict[str, str]]
    specialist_outputs: list[dict[str, str]]
    final_output: dict[str, Any]
    blocked: bool
    attempts: int


class DevOpsIncidentCommandGraph:
    def __init__(
        self,
        *,
        model: str | None = None,
        planner: Invokable | None = None,
        responder: Invokable | None = None,
        max_tool_hops: int = MAX_TOOL_HOPS,
    ) -> None:
        load_dotenv()
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.max_tool_hops = max_tool_hops
        self.workflow_name = DEFAULT_WORKFLOW_NAME
        self.planner = planner or self._build_default_planner()
        self.responder = responder or self._build_default_responder()
        self.graph = self._build_graph()

    def _build_default_planner(self) -> Invokable:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required to run this project.")

        llm = ChatOpenAI(model=self.model, temperature=0)
        return llm.with_structured_output(RouteDecision)

    def _build_default_responder(self) -> Invokable:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required to run this project.")

        llm = ChatOpenAI(model=self.model, temperature=0)
        return llm.with_structured_output(FinalResponse)

    def _build_graph(self):
        memory = MemorySaver()
        workflow = StateGraph(DevOpsAgentState)
        workflow.add_node("guardrail", self.guardrail_node)
        workflow.add_node("planner", self.planner_node)
        workflow.add_node("tool_executor", self.tool_executor_node)
        workflow.add_node("rollback_specialist", self.rollback_specialist_node)
        workflow.add_node("postmortem_specialist", self.postmortem_specialist_node)
        workflow.add_node("responder", self.responder_node)
        workflow.add_edge(START, "guardrail")
        workflow.add_conditional_edges(
            "guardrail",
            self.route_after_guardrail,
            {
                "planner": "planner",
                "responder": "responder",
            },
        )
        workflow.add_conditional_edges(
            "planner",
            self.route_after_planner,
            {
                "tool_executor": "tool_executor",
                "rollback_specialist": "rollback_specialist",
                "postmortem_specialist": "postmortem_specialist",
                "responder": "responder",
            },
        )
        workflow.add_edge("tool_executor", "planner")
        workflow.add_edge("rollback_specialist", "responder")
        workflow.add_edge("postmortem_specialist", "responder")
        workflow.add_edge("responder", END)
        return workflow.compile(checkpointer=memory)

    @staticmethod
    def _today() -> str:
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def _contains_sensitive_request(user_query: str) -> bool:
        lowered = user_query.lower()
        blocked_terms = [
            "secret",
            "token",
            "password",
            "credential",
            "private key",
            "ssh key",
            "dump all env",
        ]
        return any(term in lowered for term in blocked_terms)

    def guardrail_node(self, state: DevOpsAgentState) -> DevOpsAgentState:
        user_query = state["user_query"]
        if self._contains_sensitive_request(user_query):
            return {
                "blocked": True,
                "final_output": {
                    "summary": "The request was blocked by the DevOps guardrail.",
                    "action_items": [
                        "Remove requests for secrets, credentials, or broad sensitive access.",
                        "Ask for a scoped operational investigation instead.",
                    ],
                    "tools_used": [],
                    "escalation_needed": False,
                    "response_markdown": (
                        "## Request blocked\nThis workflow does not retrieve secrets, credentials, "
                        "or unrelated sensitive configuration."
                    ),
                },
            }
        return {"blocked": False, "specialist_outputs": []}

    def planner_node(self, state: DevOpsAgentState) -> DevOpsAgentState:
        attempts = state.get("attempts", 0)
        tool_results = state.get("tool_results", [])
        if attempts >= self.max_tool_hops:
            return {
                "route": RouteDecision(
                    action="answer",
                    query="",
                    reason="The workflow already used the maximum number of tool hops.",
                ).model_dump()
            }

        decision = self.planner.invoke(self._build_planner_prompt(state["user_query"], tool_results))
        if isinstance(decision, RouteDecision):
            route = decision
        else:
            route = RouteDecision.model_validate(decision)
        return {"route": route.model_dump()}

    def tool_executor_node(self, state: DevOpsAgentState) -> DevOpsAgentState:
        route = RouteDecision.model_validate(state["route"])
        tool = TOOL_REGISTRY[route.action]
        output = tool(route.query or state["user_query"])
        existing = state.get("tool_results", [])
        updated_results = existing + [
            {
                "tool": route.action,
                "query": route.query or state["user_query"],
                "output": output,
            }
        ]
        return {"tool_results": updated_results, "attempts": state.get("attempts", 0) + 1}

    def rollback_specialist_node(self, state: DevOpsAgentState) -> DevOpsAgentState:
        route = RouteDecision.model_validate(state["route"])
        recent_tools = state.get("tool_results", [])
        recommendation_lines = [
            "Validate whether the error spike began immediately after the latest deployment.",
            "Compare the latest release against the prior stable version for config, image, and probe changes.",
            "If blast radius is growing or customer impact is sustained, prepare rollback to the last known good release.",
        ]
        if any("connection pool" in item["output"].lower() for item in recent_tools):
            recommendation_lines.append(
                "Check whether rollback alone is sufficient or whether database pool settings also need to be restored."
            )
        output = {
            "specialist": "rollback_analysis",
            "reason": route.reason,
            "output": "\n".join(f"- {line}" for line in recommendation_lines),
        }
        return {"specialist_outputs": state.get("specialist_outputs", []) + [output]}

    def postmortem_specialist_node(self, state: DevOpsAgentState) -> DevOpsAgentState:
        route = RouteDecision.model_validate(state["route"])
        output = {
            "specialist": "draft_postmortem",
            "reason": route.reason,
            "output": (
                "- Incident summary: describe the customer impact and detection signal.\n"
                "- Timeline: deployment start, first alert, mitigation, and recovery.\n"
                "- Root cause candidates: release regression, dependency saturation, or probe misconfiguration.\n"
                "- Follow-up items: testing gaps, rollout safeguards, and observability improvements."
            ),
        }
        return {"specialist_outputs": state.get("specialist_outputs", []) + [output]}

    def responder_node(self, state: DevOpsAgentState) -> DevOpsAgentState:
        if state.get("blocked"):
            return state

        route = RouteDecision.model_validate(
            state.get("route")
            or RouteDecision(action="answer", query="", reason="No route was required.").model_dump()
        )
        response = self.responder.invoke(
            self._build_responder_prompt(
                state["user_query"],
                route.model_dump(),
                state.get("tool_results", []),
                state.get("specialist_outputs", []),
            )
        )
        if isinstance(response, FinalResponse):
            final = response
        else:
            final = FinalResponse.model_validate(response)
        return {"final_output": final.model_dump()}

    def route_after_guardrail(self, state: DevOpsAgentState) -> str:
        return "responder" if state.get("blocked") else "planner"

    def route_after_planner(self, state: DevOpsAgentState) -> str:
        route = RouteDecision.model_validate(state["route"])
        if route.action in TOOL_REGISTRY:
            return "tool_executor"
        if route.action == "rollback_analysis":
            return "rollback_specialist"
        if route.action == "draft_postmortem":
            return "postmortem_specialist"
        return "responder"

    def _build_planner_prompt(
        self,
        user_query: str,
        tool_results: list[dict[str, str]],
    ) -> str:
        return (
            f"Current date: {self._today()}\n"
            "You are a DevOps incident planner inside a LangGraph workflow.\n"
            "Allowed scope: DevOps incident triage, runbooks, infrastructure docs, incident history, "
            "and optional public web search.\n"
            "Choose exactly one next action.\n"
            "Use tools only when more evidence is needed.\n"
            "Choose `answer` when you can respond directly.\n"
            "Choose `escalate` when a human operator should take over.\n"
            "Choose `rollback_analysis` when the operator needs rollback-specific mitigation guidance.\n"
            "Choose `draft_postmortem` when the operator wants a postmortem outline or incident write-up.\n"
            f"Available actions: {', '.join(list(TOOL_REGISTRY.keys()) + ['rollback_analysis', 'draft_postmortem', 'answer', 'escalate'])}\n\n"
            f"User query:\n{user_query}\n\n"
            "Tool results collected so far:\n"
            f"{json.dumps(tool_results, indent=2)}"
        )

    def _build_responder_prompt(
        self,
        user_query: str,
        route_decision: dict[str, Any],
        tool_results: list[dict[str, str]],
        specialist_outputs: list[dict[str, str]],
    ) -> str:
        return (
            f"Current date: {self._today()}\n"
            "You are a DevOps incident responder.\n"
            "Write a concise incident response.\n"
            "Be explicit about what was searched, what likely happened, and whether escalation is needed.\n\n"
            f"User query:\n{user_query}\n\n"
            "Final route decision:\n"
            f"{json.dumps(route_decision, indent=2)}\n\n"
            "Tool results:\n"
            f"{json.dumps(tool_results, indent=2)}\n\n"
            "Specialist outputs:\n"
            f"{json.dumps(specialist_outputs, indent=2)}"
        )

    def run(self, user_query: str, *, thread_id: str = "default") -> WorkflowRunResult:
        final_state = self.graph.invoke(
            {
                "user_query": user_query,
                "tool_results": [],
                "specialist_outputs": [],
                "attempts": 0,
            },
            config={"configurable": {"thread_id": thread_id}},
        )
        final_output = final_state["final_output"]
        return WorkflowRunResult(
            user_query=user_query,
            model=self.model,
            workflow_name=self.workflow_name,
            final_output=final_output,
            tool_hops=len(final_state.get("tool_results", [])),
        )

    def get_mermaid_graph(self) -> str:
        return self.graph.get_graph().draw_mermaid()
