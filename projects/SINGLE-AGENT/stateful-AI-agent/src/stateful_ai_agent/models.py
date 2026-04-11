from __future__ import annotations

from dataclasses import dataclass
from pydantic import BaseModel, Field


class MarketResearchResult(BaseModel):
    subject: str = Field(
        description="The company, market, or business topic the answer is about."
    )
    verdict: str = Field(
        description="Short verdict prefix such as FACT, ESTIMATE, or UNKNOWN."
    )
    summary: str = Field(
        description="A concise answer to the user's question."
    )
    memory_note: str = Field(
        description="How prior session context affected this answer."
    )


@dataclass(frozen=True)
class AgentResponse:
    answer: MarketResearchResult
    model: str
    session_enabled: bool
    session_id: str | None = None
    history_items: int = 0

    def to_dict(self) -> dict[str, str | bool | int | dict[str, str] | None]:
        return {
            "answer": self.answer.model_dump(),
            "model": self.model,
            "session_enabled": self.session_enabled,
            "session_id": self.session_id,
            "history_items": self.history_items,
        }
