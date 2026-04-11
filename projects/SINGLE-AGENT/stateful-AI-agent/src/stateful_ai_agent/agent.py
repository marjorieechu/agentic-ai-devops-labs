from __future__ import annotations

import asyncio
import inspect
import os
from pathlib import Path

from agents import Agent, Runner, SQLiteSession
from dotenv import load_dotenv

from stateful_ai_agent.models import AgentResponse, MarketResearchResult


DEFAULT_MODEL = "gpt-5.4-mini"
DEFAULT_INSTRUCTIONS = """
Context:
You are a memory-enabled market research assistant.

Instructions:
- Answer business, company, industry, and competitor questions clearly and directly.
- Use the running conversation history when the user asks follow-up questions such as
  "how does that compare to last year?" or "tell me more about that trend".
- If the user refers to earlier context with words like "that", "it", or "the previous one",
  resolve the reference from session history when possible.
- Do not claim to have used tools or web search unless you were actually given those capabilities.
- If you are unsure, say so plainly instead of inventing data.

Output:
- Return structured output.
- Keep the summary concise and practical.
""".strip()


class StatefulAgent:
    def __init__(
        self,
        *,
        model: str | None = None,
        instructions: str | None = None,
        session_id: str = "stateful_demo",
        db_path: Path | str = Path("data/session.db"),
        stateless: bool = False,
    ) -> None:
        load_dotenv()

        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.instructions = instructions or DEFAULT_INSTRUCTIONS
        self.session_id = session_id
        self.db_path = Path(db_path)
        self.stateless = stateless

        self.agent = Agent(
            name="Stateful Market Research Assistant",
            instructions=self.instructions,
            model=self.model,
            output_type=MarketResearchResult,
        )
        self.session = None
        if not self.stateless:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.session = SQLiteSession(
                session_id=self.session_id,
                db_path=str(self.db_path),
            )

    def respond(self, user_input: str) -> AgentResponse:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is required to run this project with the OpenAI Agents SDK."
            )

        result = Runner.run_sync(
            self.agent,
            user_input,
            session=self.session,
        )

        history_items = 0
        if self.session is not None:
            history_items = len(self._run_async(self.session.get_items()))

        return AgentResponse(
            answer=result.final_output_as(MarketResearchResult),
            model=self.model,
            session_enabled=self.session is not None,
            session_id=self.session_id if self.session is not None else None,
            history_items=history_items,
        )

    def clear_session(self) -> None:
        if self.session is not None:
            self._run_async(self.session.clear_session())

    @staticmethod
    def _run_async(coro: object) -> object:
        if not inspect.isawaitable(coro):
            return coro
        try:
            return asyncio.run(coro)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
