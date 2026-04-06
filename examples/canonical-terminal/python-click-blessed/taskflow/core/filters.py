from __future__ import annotations

from datetime import datetime, timezone

from taskflow.core.models import Job, JobStatus


def _normalize_status(status: JobStatus | str | None) -> JobStatus | None:
    if status is None or status == "":
        return None
    if isinstance(status, JobStatus):
        return status
    return JobStatus(status)


def filter_jobs(jobs: list[Job], status: JobStatus | str | None = None, tag: str | None = None) -> list[Job]:
    selected = jobs
    normalized_status = _normalize_status(status)
    if normalized_status is not None:
        selected = [job for job in selected if job.status is normalized_status]
    if tag:
        selected = [job for job in selected if tag in job.tags]
    return list(selected)


def sort_jobs(jobs: list[Job], by: str = "started_at") -> list[Job]:
    if by == "name":
        return sorted(jobs, key=lambda job: job.name)
    if by == "status":
        return sorted(jobs, key=lambda job: (job.status.value, job.name))

    min_time = datetime.min.replace(tzinfo=timezone.utc)
    return sorted(
        jobs,
        key=lambda job: (job.started_at or min_time, job.name),
        reverse=True,
    )

