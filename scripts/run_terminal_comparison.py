from __future__ import annotations

import argparse
import sys
from typing import Callable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from verification.terminal.comparison import (
    compare_filtered_status_outputs,
    compare_inspect_outputs,
    compare_list_outputs,
    compare_stats_outputs,
    run_comparison_op,
)
from verification.terminal.registry import TERMINAL_EXAMPLES


ComparisonFn = Callable[[list], dict]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare terminal examples across languages.")
    parser.add_argument("--verbose", action="store_true", help="Print mismatch details and commands.")
    parser.add_argument("--example", action="append", default=[], help="Restrict comparison to one named example.")
    return parser


def select_examples(names: list[str]):
    if not names:
        return list(TERMINAL_EXAMPLES)
    known = {example.name: example for example in TERMINAL_EXAMPLES}
    missing = [name for name in names if name not in known]
    if missing:
        raise SystemExit(f"unknown example(s): {', '.join(missing)}")
    return [known[name] for name in names]


def _summary_counts(summary: dict) -> tuple[int, int, int]:
    consistent = mismatches = skipped = 0
    for entry in summary["results"].values():
        if entry.get("skipped"):
            skipped += 1
        elif entry.get("match"):
            consistent += 1
        else:
            mismatches += 1
    return consistent, mismatches, skipped


def _detail_suffix(entry: dict) -> str:
    if entry.get("skipped"):
        reason = entry.get("reason") or "not available"
        return f"(not installed: {reason})"
    if "count" in entry:
        return f"count={entry['count']}"
    if "total" in entry:
        return f"total={entry['total']}"
    if "id" in entry:
        return f"id={entry['id']!r}"
    if "statuses" in entry:
        return f"statuses={entry['statuses']}"
    if "parse_error" in entry:
        return entry["parse_error"]
    return "no result details"


def _print_summary(label: str, summary: dict, *, verbose: bool, results: list) -> bool:
    print(f"Comparison: {label}")
    result_map = {result.example_name: result for result in results}
    for name, entry in summary["results"].items():
        if entry.get("skipped"):
            marker = "○"
        elif entry.get("match"):
            marker = "✓"
        else:
            marker = "✗"
        print(f"{marker} {name:<28} {_detail_suffix(entry)}")
        if verbose and name in result_map:
            print(f"  command: {' '.join(result_map[name].command)}")
            if entry.get("parse_error"):
                print(f"  error: {entry['parse_error']}")

    consistent, mismatches, skipped = _summary_counts(summary)
    print(f"Summary: {consistent}/{len(summary['results'])} consistent, {mismatches} mismatch, {skipped} skipped")
    if verbose and summary["mismatches"]:
        for mismatch in summary["mismatches"]:
            print(f"  mismatch: {mismatch}")
    print()
    return not summary["mismatches"]


def _run_and_report(
    examples,
    command_template: list[str],
    label: str,
    compare: ComparisonFn,
    *,
    verbose: bool,
) -> bool:
    results = run_comparison_op(examples, command_template, {})
    summary = compare(results)
    return _print_summary(label, summary, verbose=verbose, results=results)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    examples = select_examples(args.example)

    checks = [
        (
            ["taskflow", "list", "--output", "json"],
            "taskflow list --output json",
            compare_list_outputs,
        ),
        (
            ["taskflow", "stats", "--output", "json"],
            "taskflow stats --output json",
            compare_stats_outputs,
        ),
        (
            ["taskflow", "inspect", "job-001", "--output", "json"],
            'taskflow inspect job-001 --output json',
            lambda results: compare_inspect_outputs(results, "job-001"),
        ),
        (
            ["taskflow", "list", "--status", "done", "--output", "json"],
            'taskflow list --status done --output json',
            lambda results: compare_filtered_status_outputs(results, expected_status="done"),
        ),
    ]

    success = True
    for command_template, label, compare in checks:
        success = _run_and_report(
            examples,
            command_template,
            label,
            compare,
            verbose=args.verbose,
        ) and success

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
