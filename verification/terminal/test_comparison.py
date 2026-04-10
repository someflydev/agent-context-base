from __future__ import annotations

import unittest

from verification.terminal.comparison import (
    compare_filtered_status_outputs,
    compare_inspect_outputs,
    compare_list_outputs,
    compare_stats_outputs,
    run_comparison_op,
)
from verification.terminal.registry import TERMINAL_EXAMPLES


class TestCrossLanguageComparison(unittest.TestCase):
    def _run(self, command_template: list[str]):
        return run_comparison_op(TERMINAL_EXAMPLES, command_template, {})

    def _require_available_results(self, results):
        available = [result for result in results if not result.skipped]
        if not available:
            self.skipTest("no terminal examples are available in this environment")
        return available

    def test_list_json_count_consistent(self):
        """
        All available examples should return 20 jobs for list --output json.
        Skip examples that are not installed/available.
        Assert all available examples agree on count.
        """

        results = self._run(["taskflow", "list", "--output", "json"])
        self._require_available_results(results)
        summary = compare_list_outputs(results)

        for result in results:
            with self.subTest(example=result.example_name):
                if result.skipped:
                    continue
                self.assertTrue(
                    summary["results"][result.example_name]["match"],
                    summary["results"][result.example_name],
                )

        self.assertTrue(summary["all_match"], summary["mismatches"])

    def test_stats_total_consistent(self):
        """
        All available examples should return total=20 for stats --output json.
        """

        results = self._run(["taskflow", "stats", "--output", "json"])
        self._require_available_results(results)
        summary = compare_stats_outputs(results)

        for result in results:
            with self.subTest(example=result.example_name):
                if result.skipped:
                    continue
                self.assertTrue(
                    summary["results"][result.example_name]["match"],
                    summary["results"][result.example_name],
                )

        self.assertTrue(summary["all_match"], summary["mismatches"])

    def test_inspect_job001_id_consistent(self):
        """
        All available examples should return id="job-001" for inspect job-001.
        """

        results = self._run(["taskflow", "inspect", "job-001", "--output", "json"])
        self._require_available_results(results)
        summary = compare_inspect_outputs(results, "job-001")

        for result in results:
            with self.subTest(example=result.example_name):
                if result.skipped:
                    continue
                self.assertTrue(
                    summary["results"][result.example_name]["match"],
                    summary["results"][result.example_name],
                )

        self.assertTrue(summary["all_match"], summary["mismatches"])

    def test_filter_done_all_status_done(self):
        """
        All available examples: list --status done --output json
        → all returned items have status "done"
        """

        results = self._run(["taskflow", "list", "--status", "done", "--output", "json"])
        self._require_available_results(results)
        summary = compare_filtered_status_outputs(results, expected_status="done")

        for result in results:
            with self.subTest(example=result.example_name):
                if result.skipped:
                    continue
                self.assertTrue(
                    summary["results"][result.example_name]["match"],
                    summary["results"][result.example_name],
                )

        self.assertTrue(summary["all_match"], summary["mismatches"])


if __name__ == "__main__":
    unittest.main()
