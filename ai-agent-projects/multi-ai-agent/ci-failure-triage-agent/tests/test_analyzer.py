import unittest

from ci_failure_triage_agent.analyzer import analyze_log


class AnalyzerTests(unittest.TestCase):
    def test_classifies_test_failure(self) -> None:
        log = """
        FAILED tests/test_orders.py::test_create_order - AssertionError
        E       AssertionError: expected 201 got 500
        Error: Process completed with exit code 1.
        """

        result = analyze_log(log)

        self.assertEqual(result.category, "test_failure")
        self.assertEqual(result.severity, "medium")
        self.assertEqual(result.confidence, "high")

    def test_classifies_dependency_failure(self) -> None:
        log = """
        Run pip install -r requirements.txt
        ERROR: Could not find a version that satisfies the requirement private-package==1.2.3
        ERROR: No matching distribution found for private-package==1.2.3
        """

        result = analyze_log(log)

        self.assertEqual(result.category, "dependency_install_failure")
        self.assertEqual(result.severity, "high")

    def test_falls_back_to_unknown_failure(self) -> None:
        log = """
        The command exited unexpectedly.
        Process terminated.
        """

        result = analyze_log(log)

        self.assertEqual(result.category, "unknown_failure")
        self.assertEqual(result.confidence, "low")


if __name__ == "__main__":
    unittest.main()
