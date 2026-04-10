from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Any

from verification.terminal.harness import TerminalExample


EXPECTED_JOB_COUNT = 20
COMMAND_TIMEOUT_S = 30


@dataclass
class ComparisonResult:
    example_name: str
    command: list[str]
    exit_code: int | None
    output: str
    parsed: Any
    parse_error: str | None
    skipped: bool = False
    skip_reason: str | None = None


def _check_example_available(example: TerminalExample) -> tuple[bool, str | None]:
    if not example.path.exists():
        return False, f"example path does not exist: {example.path}"
    if example.availability_check is not None:
        available, reason = example.availability_check()
        if not available:
            return False, reason
    if example.fixture_validator is not None:
        fixtures_ok, reason = example.fixture_validator()
        if not fixtures_ok:
            return False, reason
    return True, None


def _extract_fixture_args(example: TerminalExample) -> list[str]:
    tokens = example.smoke_cmd
    if "list" not in tokens:
        return []
    command_tokens = tokens[tokens.index("list") + 1 :]
    fixture_args: list[str] = []
    index = 0
    while index < len(command_tokens):
        token = command_tokens[index]
        if token == "--fixtures-path" and index + 1 < len(command_tokens):
            fixture_args.extend(command_tokens[index : index + 2])
            index += 2
            continue
        index += 1
    return fixture_args


def _build_example_command(example: TerminalExample, command_template: list[str]) -> list[str]:
    if not command_template:
        raise ValueError("command_template must not be empty")

    template = list(command_template)
    if template[0] == "taskflow":
        template = template[1:]
    if not template:
        raise ValueError("command_template must include a taskflow subcommand")

    if "list" not in example.smoke_cmd:
        raise ValueError(f"example {example.name} smoke command does not contain 'list'")

    base_command = example.smoke_cmd[: example.smoke_cmd.index("list")]
    return [*base_command, *template, *_extract_fixture_args(example)]


def run_comparison_op(
    examples: list[TerminalExample],
    command_template: list[str],
    fixtures_env: dict[str, str] | None = None,
) -> list[ComparisonResult]:
    """
    Run command_template against each available example.
    command_template: e.g. ["taskflow", "list", "--output", "json"]
    Returns one ComparisonResult per example.
    """

    results: list[ComparisonResult] = []
    fixture_env = fixtures_env or {}

    for example in examples:
        available, reason = _check_example_available(example)
        command = _build_example_command(example, command_template)
        if not available:
            results.append(
                ComparisonResult(
                    example_name=example.name,
                    command=command,
                    exit_code=None,
                    output="",
                    parsed=None,
                    parse_error=None,
                    skipped=True,
                    skip_reason=reason,
                )
            )
            continue

        env = os.environ.copy()
        env.update(example.fixtures_env)
        env.update(example.extra_env)
        env.update(fixture_env)

        try:
            completed = subprocess.run(
                command,
                cwd=example.path,
                env=env,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_S,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            results.append(
                ComparisonResult(
                    example_name=example.name,
                    command=command,
                    exit_code=None,
                    output=(error.stdout or "").strip(),
                    parsed=None,
                    parse_error=f"command timed out after {COMMAND_TIMEOUT_S} seconds",
                )
            )
            continue

        output = completed.stdout.strip()
        parsed: Any = None
        parse_error: str | None = None
        if completed.returncode == 0:
            try:
                parsed = json.loads(output)
            except json.JSONDecodeError as error:
                parse_error = f"invalid JSON output: {error.msg}"
        else:
            parse_error = (completed.stderr.strip() or f"command exited with {completed.returncode}")

        results.append(
            ComparisonResult(
                example_name=example.name,
                command=command,
                exit_code=completed.returncode,
                output=output,
                parsed=parsed,
                parse_error=parse_error,
            )
        )

    return results


def _base_summary(expected_key: str, expected_value: Any) -> dict[str, Any]:
    return {
        expected_key: expected_value,
        "results": {},
        "all_match": True,
        "mismatches": [],
        "skipped": [],
    }


def compare_list_outputs(results: list[ComparisonResult]) -> dict[str, Any]:
    """
    Compare list --output json results across examples.
    Returns:
      {
        "expected_count": 20,
        "results": {
          "python-typer-textual": {"count": 20, "match": True},
          "rust-clap-ratatui":    {"count": 20, "match": True},
          ...
        },
        "all_match": True,
        "mismatches": []
      }
    """

    summary = _base_summary("expected_count", EXPECTED_JOB_COUNT)
    for result in results:
        if result.skipped:
            summary["results"][result.example_name] = {
                "skipped": True,
                "reason": result.skip_reason,
            }
            summary["skipped"].append(result.example_name)
            continue

        entry: dict[str, Any] = {"match": False}
        if result.parse_error is not None:
            entry["parse_error"] = result.parse_error
            summary["mismatches"].append(f"{result.example_name}: {result.parse_error}")
        elif not isinstance(result.parsed, list):
            entry["parse_error"] = "expected a JSON list"
            summary["mismatches"].append(f"{result.example_name}: expected a JSON list")
        else:
            entry["count"] = len(result.parsed)
            entry["match"] = len(result.parsed) == EXPECTED_JOB_COUNT
            if not entry["match"]:
                summary["mismatches"].append(
                    f"{result.example_name}: expected {EXPECTED_JOB_COUNT} jobs, got {len(result.parsed)}"
                )
        summary["results"][result.example_name] = entry

    summary["all_match"] = not summary["mismatches"]
    return summary


def compare_stats_outputs(results: list[ComparisonResult]) -> dict[str, Any]:
    """
    Compare stats --output json results across examples.
    Assert: total == 20 across all implementations.
    """

    summary = _base_summary("expected_total", EXPECTED_JOB_COUNT)
    for result in results:
        if result.skipped:
            summary["results"][result.example_name] = {
                "skipped": True,
                "reason": result.skip_reason,
            }
            summary["skipped"].append(result.example_name)
            continue

        entry: dict[str, Any] = {"match": False}
        if result.parse_error is not None:
            entry["parse_error"] = result.parse_error
            summary["mismatches"].append(f"{result.example_name}: {result.parse_error}")
        elif not isinstance(result.parsed, dict):
            entry["parse_error"] = "expected a JSON object"
            summary["mismatches"].append(f"{result.example_name}: expected a JSON object")
        else:
            total = result.parsed.get("total")
            entry["total"] = total
            entry["match"] = total == EXPECTED_JOB_COUNT
            if not entry["match"]:
                summary["mismatches"].append(
                    f"{result.example_name}: expected total={EXPECTED_JOB_COUNT}, got {total!r}"
                )
        summary["results"][result.example_name] = entry

    summary["all_match"] = not summary["mismatches"]
    return summary


def compare_inspect_outputs(results: list[ComparisonResult], job_id: str) -> dict[str, Any]:
    """
    Compare inspect <job_id> --output json results across examples.
    Assert: id == job_id in all results.
    """

    summary = _base_summary("expected_id", job_id)
    for result in results:
        if result.skipped:
            summary["results"][result.example_name] = {
                "skipped": True,
                "reason": result.skip_reason,
            }
            summary["skipped"].append(result.example_name)
            continue

        entry: dict[str, Any] = {"match": False}
        if result.parse_error is not None:
            entry["parse_error"] = result.parse_error
            summary["mismatches"].append(f"{result.example_name}: {result.parse_error}")
        elif not isinstance(result.parsed, dict):
            entry["parse_error"] = "expected a JSON object"
            summary["mismatches"].append(f"{result.example_name}: expected a JSON object")
        else:
            found_id = result.parsed.get("id")
            entry["id"] = found_id
            entry["match"] = found_id == job_id
            if not entry["match"]:
                summary["mismatches"].append(
                    f"{result.example_name}: expected id={job_id}, got {found_id!r}"
                )
        summary["results"][result.example_name] = entry

    summary["all_match"] = not summary["mismatches"]
    return summary


def compare_filtered_status_outputs(
    results: list[ComparisonResult],
    *,
    expected_status: str,
) -> dict[str, Any]:
    summary = _base_summary("expected_status", expected_status)
    for result in results:
        if result.skipped:
            summary["results"][result.example_name] = {
                "skipped": True,
                "reason": result.skip_reason,
            }
            summary["skipped"].append(result.example_name)
            continue

        entry: dict[str, Any] = {"match": False}
        if result.parse_error is not None:
            entry["parse_error"] = result.parse_error
            summary["mismatches"].append(f"{result.example_name}: {result.parse_error}")
        elif not isinstance(result.parsed, list):
            entry["parse_error"] = "expected a JSON list"
            summary["mismatches"].append(f"{result.example_name}: expected a JSON list")
        else:
            statuses = sorted({item.get("status") for item in result.parsed if isinstance(item, dict)})
            entry["count"] = len(result.parsed)
            entry["statuses"] = statuses
            entry["match"] = all(
                isinstance(item, dict) and item.get("status") == expected_status for item in result.parsed
            )
            if not entry["match"]:
                summary["mismatches"].append(
                    f"{result.example_name}: filtered list contains statuses {statuses}"
                )
        summary["results"][result.example_name] = entry

    summary["all_match"] = not summary["mismatches"]
    return summary
