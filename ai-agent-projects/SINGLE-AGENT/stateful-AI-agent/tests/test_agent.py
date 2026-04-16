from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from stateful_ai_agent.agent import StatefulAgent
from stateful_ai_agent.models import MarketResearchResult


class StatefulAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ.pop("OPENAI_MODEL", None)

    def tearDown(self) -> None:
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("OPENAI_MODEL", None)

    @patch("stateful_ai_agent.agent.load_dotenv")
    @patch("stateful_ai_agent.agent.SQLiteSession")
    @patch("stateful_ai_agent.agent.Runner.run_sync")
    def test_stateful_agent_uses_sqlite_session(
        self,
        mock_run_sync: MagicMock,
        mock_sqlite_session: MagicMock,
        _mock_load_dotenv: MagicMock,
    ) -> None:
        session = MagicMock()
        session.get_items.return_value = [{"role": "user"}, {"role": "assistant"}]
        mock_sqlite_session.return_value = session
        run_result = MagicMock()
        run_result.final_output_as.return_value = MarketResearchResult(
            subject="Tesla",
            verdict="FACT",
            summary="Tesla remains the active subject in this conversation.",
            memory_note="The agent used session history to resolve the follow-up reference.",
        )
        mock_run_sync.return_value = run_result

        agent = StatefulAgent(
            session_id="memory_demo",
            db_path=Path("tests/.tmp/session.db"),
        )
        response = agent.respond("How does that compare to last year?")

        self.assertTrue(response.session_enabled)
        self.assertEqual(response.session_id, "memory_demo")
        self.assertEqual(response.model, "gpt-5.4-mini")
        self.assertEqual(response.history_items, 2)
        self.assertEqual(response.answer.subject, "Tesla")
        self.assertEqual(response.answer.verdict, "FACT")
        self.assertEqual(mock_run_sync.call_args.kwargs["session"], session)
        run_result.final_output_as.assert_called_once_with(MarketResearchResult)

    @patch("stateful_ai_agent.agent.Runner.run_sync")
    @patch("stateful_ai_agent.agent.load_dotenv")
    def test_stateless_agent_disables_session(
        self,
        _mock_load_dotenv: MagicMock,
        mock_run_sync: MagicMock,
    ) -> None:
        run_result = MagicMock()
        run_result.final_output_as.return_value = MarketResearchResult(
            subject="Unknown",
            verdict="UNKNOWN",
            summary="I cannot resolve the follow-up without prior context.",
            memory_note="No session memory was enabled for this run.",
        )
        mock_run_sync.return_value = run_result

        agent = StatefulAgent(stateless=True)
        response = agent.respond("How does that compare to last year?")

        self.assertFalse(response.session_enabled)
        self.assertIsNone(response.session_id)
        self.assertEqual(response.history_items, 0)
        self.assertEqual(mock_run_sync.call_args.kwargs["session"], None)
        self.assertEqual(response.answer.verdict, "UNKNOWN")

    @patch("stateful_ai_agent.agent.load_dotenv")
    @patch("stateful_ai_agent.agent.SQLiteSession")
    def test_clear_session_calls_sdk_session_clear(
        self,
        mock_sqlite_session: MagicMock,
        _mock_load_dotenv: MagicMock,
    ) -> None:
        session = MagicMock()
        mock_sqlite_session.return_value = session

        agent = StatefulAgent(
            session_id="clearable_demo",
            db_path=Path("tests/.tmp/clearable.db"),
        )

        agent.clear_session()

        session.clear_session.assert_called_once()

    @patch("stateful_ai_agent.agent.load_dotenv")
    def test_missing_api_key_raises_clear_error(self, _mock_load_dotenv: MagicMock) -> None:
        os.environ.pop("OPENAI_API_KEY", None)
        agent = StatefulAgent(stateless=True)

        with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY is required"):
            agent.respond("Hello")


if __name__ == "__main__":
    unittest.main()
