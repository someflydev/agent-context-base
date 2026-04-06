from __future__ import annotations

import json
from pathlib import Path

import click
from blessed import Terminal

from taskflow.core.filters import filter_jobs, sort_jobs
from taskflow.core.loader import FixtureError, default_fixtures_path, load_jobs
from taskflow.core.stats import compute_stats
from taskflow.interactive.pager import run_pager


term = Terminal()


def _resolve_fixtures_path(fixtures_path: str | None) -> Path:
    return Path(fixtures_path).expanduser().resolve() if fixtures_path else default_fixtures_path()


def _print_marker_block(begin: str, content: str, end: str) -> None:
    click.echo(begin)
    if content:
        click.echo(content)
    click.echo(end)


def _status_label(status: str) -> str:
    palette = {
        "done": term.green(status),
        "failed": term.red(status),
        "running": term.yellow(status),
        "pending": term.white(status),
    }
    return palette.get(status, status)


def _jobs_table(jobs: list, color: bool = False) -> str:
    lines = [f"{'ID':<8} {'NAME':<24} {'STATUS':<8} {'STARTED_AT':<20} TAGS"]
    for job in jobs:
        started = job.started_at.isoformat().replace("+00:00", "Z") if job.started_at else "-"
        status = _status_label(job.status.value) if color else job.status.value
        lines.append(f"{job.id:<8} {job.name:<24} {status:<8} {started:<20} {','.join(job.tags)}")
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


def _abort_with_error(error: str) -> None:
    _print_marker_block("## BEGIN_ERROR ##", error, "## END_ERROR ##")
    raise click.ClickException(error)


@click.group()
def app() -> None:
    """TaskFlow Monitor CLI."""


@app.command("list")
@click.option("--status")
@click.option("--tag")
@click.option("--output", type=click.Choice(["json", "table"]), default="table")
@click.option("--fixtures-path", type=click.Path(path_type=Path))
def list_jobs(status: str | None, tag: str | None, output: str, fixtures_path: Path | None) -> None:
    try:
        jobs = sort_jobs(filter_jobs(load_jobs(_resolve_fixtures_path(str(fixtures_path) if fixtures_path else None)), status=status, tag=tag))
    except FixtureError as error:
        _abort_with_error(str(error))
    if output == "json":
        click.echo(json.dumps([job.to_dict() for job in jobs], indent=2))
        return
    _print_marker_block("## BEGIN_JOBS ##", _jobs_table(jobs), "## END_JOBS ##")


@app.command()
@click.argument("job_id")
@click.option("--output", type=click.Choice(["json", "plain"]), default="plain")
@click.option("--fixtures-path", type=click.Path(path_type=Path))
def inspect(job_id: str, output: str, fixtures_path: Path | None) -> None:
    try:
        jobs = load_jobs(_resolve_fixtures_path(str(fixtures_path) if fixtures_path else None))
    except FixtureError as error:
        _abort_with_error(str(error))
    job = next((item for item in jobs if item.id == job_id), None)
    if job is None:
        _abort_with_error(f"job not found: {job_id}")
    if output == "json":
        click.echo(json.dumps(job.to_dict(), indent=2))
        return
    _print_marker_block("## BEGIN_JOB_DETAIL ##", _job_plain(job), "## END_JOB_DETAIL ##")


@app.command()
@click.option("--output", type=click.Choice(["json", "plain"]), default="plain")
@click.option("--fixtures-path", type=click.Path(path_type=Path))
def stats(output: str, fixtures_path: Path | None) -> None:
    try:
        stats_model = compute_stats(load_jobs(_resolve_fixtures_path(str(fixtures_path) if fixtures_path else None)))
    except FixtureError as error:
        _abort_with_error(str(error))
    if output == "json":
        click.echo(json.dumps(stats_model.to_dict(), indent=2))
        return
    _print_marker_block("## BEGIN_STATS ##", _stats_plain(stats_model), "## END_STATS ##")


@app.command()
@click.option("--interval", type=int, default=5)
@click.option("--no-tui", is_flag=True, default=False)
@click.option("--fixtures-path", type=click.Path(path_type=Path))
def watch(interval: int, no_tui: bool, fixtures_path: Path | None) -> None:
    del interval
    resolved = _resolve_fixtures_path(str(fixtures_path) if fixtures_path else None)
    try:
        jobs = sort_jobs(load_jobs(resolved))
    except FixtureError as error:
        _abort_with_error(str(error))
    if no_tui:
        _print_marker_block("## BEGIN_JOBS ##", _jobs_table(jobs), "## END_JOBS ##")
        return
    run_pager(jobs)


def main() -> None:
    app()

