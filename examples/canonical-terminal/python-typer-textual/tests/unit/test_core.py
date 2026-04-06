from pathlib import Path

from taskflow.core.filters import filter_jobs, sort_jobs
from taskflow.core.loader import default_fixtures_path, load_config, load_jobs
from taskflow.core.stats import compute_stats


def test_load_jobs_reads_shared_fixture_set() -> None:
    jobs = load_jobs(default_fixtures_path())
    assert len(jobs) == 20
    assert jobs[0].id == "job-001"


def test_filter_jobs_by_status() -> None:
    jobs = load_jobs(default_fixtures_path())
    failed = filter_jobs(jobs, status="failed")
    assert len(failed) == 4
    assert all(job.status.value == "failed" for job in failed)


def test_filter_jobs_by_tag() -> None:
    jobs = load_jobs(default_fixtures_path())
    frontend = filter_jobs(jobs, tag="frontend")
    assert frontend
    assert all("frontend" in job.tags for job in frontend)


def test_sort_jobs_defaults_to_recent_started_at() -> None:
    jobs = load_jobs(default_fixtures_path())
    sorted_jobs = sort_jobs(jobs)
    assert sorted_jobs[0].id == "job-012"
    assert sorted_jobs[-1].id in {"job-013", "job-014", "job-015", "job-016"}


def test_compute_stats_matches_fixture_distribution() -> None:
    jobs = load_jobs(default_fixtures_path())
    stats = compute_stats(jobs)
    assert stats.total == 20
    assert stats.by_status == {"pending": 4, "running": 3, "done": 9, "failed": 4}
    assert stats.failure_rate == 0.2


def test_load_config_reads_fixture_mode() -> None:
    config = load_config(Path(default_fixtures_path()))
    assert config["fixture_mode"] is True

