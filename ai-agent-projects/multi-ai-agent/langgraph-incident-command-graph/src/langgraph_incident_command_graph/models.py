from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field


ToolAction = Literal[
    "search_runbooks",
    "search_incident_history",
    "search_infrastructure_docs",
    "search_live_web",
    "rollback_analysis",
    "draft_postmortem",
    "answer",
    "escalate",
]


class RouteDecision(BaseModel):
    action: ToolAction = Field(description="The next action the agent should take.")
    query: str = Field(
        default="",
        description="The query to send to the selected tool. Empty when answering directly.",
    )
    reason: str = Field(description="Short explanation for why this action was selected.")


class FinalResponse(BaseModel):
    summary: str = Field(description="Brief incident summary for the operator.")
    action_items: list[str] = Field(description="Recommended next actions.")
    tools_used: list[str] = Field(description="Tools the workflow used before responding.")
    escalation_needed: bool = Field(description="Whether a human escalation is recommended.")
    response_markdown: str = Field(description="Markdown response to present to the user.")


@dataclass(frozen=True)
class WorkflowRunResult:
    user_query: str
    model: str
    workflow_name: str
    final_output: dict[str, object]
    tool_hops: int

    def to_dict(self) -> dict[str, object]:
        return {
            "user_query": self.user_query,
            "model": self.model,
            "workflow_name": self.workflow_name,
            "tool_hops": self.tool_hops,
            "final_output": self.final_output,
        }
