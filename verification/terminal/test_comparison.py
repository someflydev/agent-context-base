from __future__ import annotations

import unittest

from verification.terminal.comparison import (
    check_example_available,
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


def _make_per_example_test(
    *,
    example,
    command_template: list[str],
    compare_fn,
    test_suffix: str,
):
    available, reason = check_example_available(example)

    def test_method(self):
        results = run_comparison_op([example], command_template, {})
        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertFalse(result.skipped, result.skip_reason)

        summary = compare_fn(results)
        self.assertTrue(
            summary["results"][example.name]["match"],
            summary["results"][example.name],
        )
        self.assertTrue(summary["all_match"], summary["mismatches"])

    test_method.__name__ = f"test_{test_suffix}_{example.name.replace('-', '_')}"
    test_method.__doc__ = f"{example.name}: {' '.join(command_template)} remains structurally consistent."
    return unittest.skipUnless(available, reason or "example is not available")(test_method)


for _example in TERMINAL_EXAMPLES:
    setattr(
        TestCrossLanguageComparison,
        f"test_list_json_per_example_{_example.name.replace('-', '_')}",
        _make_per_example_test(
            example=_example,
            command_template=["taskflow", "list", "--output", "json"],
            compare_fn=compare_list_outputs,
            test_suffix="list_json_per_example",
        ),
    )
    setattr(
        TestCrossLanguageComparison,
        f"test_stats_json_per_example_{_example.name.replace('-', '_')}",
        _make_per_example_test(
            example=_example,
            command_template=["taskflow", "stats", "--output", "json"],
            compare_fn=compare_stats_outputs,
            test_suffix="stats_json_per_example",
        ),
    )
    setattr(
        TestCrossLanguageComparison,
        f"test_inspect_job001_per_example_{_example.name.replace('-', '_')}",
        _make_per_example_test(
            example=_example,
            command_template=["taskflow", "inspect", "job-001", "--output", "json"],
            compare_fn=lambda results: compare_inspect_outputs(results, "job-001"),
            test_suffix="inspect_job001_per_example",
        ),
    )
    setattr(
        TestCrossLanguageComparison,
        f"test_list_done_json_per_example_{_example.name.replace('-', '_')}",
        _make_per_example_test(
            example=_example,
            command_template=["taskflow", "list", "--status", "done", "--output", "json"],
            compare_fn=lambda results: compare_filtered_status_outputs(results, expected_status="done"),
            test_suffix="list_done_json_per_example",
        ),
    )


if __name__ == "__main__":
    unittest.main()
