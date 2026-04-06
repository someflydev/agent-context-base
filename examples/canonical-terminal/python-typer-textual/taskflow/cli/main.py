from __future__ import annotations

import json
from pathlib import Path

import typer

from taskflow.core.filters import filter_jobs, sort_jobs
from taskflow.core.loader import FixtureError, default_fixtures_path, load_jobs
from taskflow.core.stats import compute_stats

app = typer.Typer(help="TaskFlow Monitor CLI")


def _resolve_fixtures_path(fixtures_path: Path | None) -> Path:
    return fixtures_path.expanduser().resolve() if fixtures_path else default_fixtures_path()


def _print_marker_block(begin: str, content: str, end: str) -> None:
    typer.echo(begin)
    if content:
        typer.echo(content)
    typer.echo(end)


def _jobs_table(jobs: list) -> str:
    lines = [f"{'ID':<8} {'NAME':<24} {'STATUS':<8} {'STARTED_AT':<20} TAGS"]
    for job in jobs:
        started = job.started_at.isoformat().replace("+00:00", "Z") if job.started_at else "-"
        tags = ",".join(job.tags)
        lines.append(f"{job.id:<8} {job.name:<24} {job.status.value:<8} {started:<20} {tags}")
    return "\n".join(lines)


def _job_plain(job) -> str:
    lines = [
        f"ID: {job.id}",
        f"Name: {job.name}",
        f"Status: {job.status.value}",
        f"Started: {job.started_at.isoformat().replace('+00:00', 'Z') if job.started_at else '-'}",
        f"Duration (s): {job.duration_s if job.duration_s is not None else '-'}",
        f"Tags: {', '.join(job.tags)}",
        "Output:",
    ]
    lines.extend(f"  - {line}" for line in job.output_lines)
    return "\n".join(lines)


def _stats_plain(stats) -> str:
    return "\n".join(
        [
            f"Total jobs: {stats.total}",
            f"Done: {stats.by_status['done']}",
            f"Failed: {stats.by_status['failed']}",
            f"Running: {stats.by_status['running']}",
            f"Pending: {stats.by_status['pending']}",
            f"Average duration (s): {stats.avg_duration_s}",
            f"Failure rate: {stats.failure_rate}",
        ]
    )


def _handle_fixture_error(error: FixtureError) -> None:
    _print_marker_block("## BEGIN_ERROR ##", str(error), "## END_ERROR ##")
    raise typer.Exit(code=1)


def _emit_jobs(
    fixtures_path: Path | None,
    status: str | None = None,
    tag: str | None = None,
    output: str = "table",
) -> None:
    try:
        jobs = sort_jobs(filter_jobs(load_jobs(_resolve_fixtures_path(fixtures_path)), status=status, tag=tag))
    except FixtureError as error:
        _handle_fixture_error(error)
    if output == "json":
        typer.echo(json.dumps([job.to_dict() for job in jobs], indent=2))
        return
    _print_marker_block("## BEGIN_JOBS ##", _jobs_table(jobs), "## END_JOBS ##")


@app.command("list")
def list_jobs(
    status: str | None = typer.Option(None, "--status"),
    tag: str | None = typer.Option(None, "--tag"),
    output: str = typer.Option("table", "--output"),
    fixtures_path: Path | None = typer.Option(None, "--fixtures-path"),
) -> None:
    _emit_jobs(fixtures_path=fixtures_path, status=status, tag=tag, output=output)


@app.command()
def inspect(
    job_id: str,
    output: str = typer.Option("plain", "--output"),
    fixtures_path: Path | None = typer.Option(None, "--fixtures-path"),
) -> None:
    try:
        jobs = load_jobs(_resolve_fixtures_path(fixtures_path))
    except FixtureError as error:
        _handle_fixture_error(error)
    job = next((item for item in jobs if item.id == job_id), None)
    if job is None:
        _print_marker_block("## BEGIN_ERROR ##", f"job not found: {job_id}", "## END_ERROR ##")
        raise typer.Exit(code=1)
    if output == "json":
        typer.echo(json.dumps(job.to_dict(), indent=2))
        return
    _print_marker_block("## BEGIN_JOB_DETAIL ##", _job_plain(job), "## END_JOB_DETAIL ##")


@app.command()
def stats(
    output: str = typer.Option("plain", "--output"),
    fixtures_path: Path | None = typer.Option(None, "--fixtures-path"),
) -> None:
    try:
        stats_model = compute_stats(load_jobs(_resolve_fixtures_path(fixtures_path)))
    except FixtureError as error:
        _handle_fixture_error(error)
    if output == "json":
        typer.echo(json.dumps(stats_model.to_dict(), indent=2))
        return
    _print_marker_block("## BEGIN_STATS ##", _stats_plain(stats_model), "## END_STATS ##")


@app.command()
def watch(
    interval: int = typer.Option(5, "--interval"),
    no_tui: bool = typer.Option(False, "--no-tui"),
    fixtures_path: Path | None = typer.Option(None, "--fixtures-path"),
) -> None:
    del interval
    if no_tui:
        _emit_jobs(fixtures_path=fixtures_path, output="table")
        return
    from taskflow.tui.app import TaskFlowApp

    app_instance = TaskFlowApp(fixtures_path=_resolve_fixtures_path(fixtures_path))
    app_instance.run()


def main() -> None:
    app()
