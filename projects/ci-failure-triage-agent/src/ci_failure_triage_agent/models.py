from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class TriageResult:
    category: str
    severity: str
    confidence: str
    summary: str
    recommended_action: str
    evidence: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
