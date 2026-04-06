import json
from pathlib import Path

from typer.testing import CliRunner

from taskflow.cli.main import app
from taskflow.core.loader import default_fixtures_path


runner = CliRunner()


def _base_args() -> list[str]:
    return ["--fixtures-path", str(default_fixtures_path())]


def test_list_table_output() -> None:
    result = runner.invoke(app, ["list", *_base_args()])
    assert result.exit_code == 0
    assert "## BEGIN_JOBS ##" in result.stdout
    assert "## END_JOBS ##" in result.stdout
    assert "build-frontend" in result.stdout


def test_list_json_output() -> None:
    result = runner.invoke(app, ["list", *_base_args(), "--output", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert len(payload) == 20


def test_list_filter_by_status() -> None:
    result = runner.invoke(app, ["list", *_base_args(), "--status", "done", "--output", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload
    assert all(job["status"] == "done" for job in payload)


def test_inspect_job() -> None:
    result = runner.invoke(app, ["inspect", "job-001", *_base_args(), "--output", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["id"] == "job-001"


def test_stats_json() -> None:
    result = runner.invoke(app, ["stats", *_base_args(), "--output", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["total"] == 20


def test_watch_no_tui() -> None:
    result = runner.invoke(app, ["watch", *_base_args(), "--no-tui"])
    assert result.exit_code == 0
    assert "## BEGIN_JOBS ##" in result.stdout


def test_list_missing_fixtures() -> None:
    missing = Path(default_fixtures_path()) / "missing-dir"
    result = runner.invoke(app, ["list", "--fixtures-path", str(missing)])
    assert result.exit_code == 1

