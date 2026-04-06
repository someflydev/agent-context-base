from __future__ import annotations

from taskflow.core.models import Job, JobStatus, Stats


def compute_stats(jobs: list[Job]) -> Stats:
    total = len(jobs)
    by_status = {status.value: 0 for status in JobStatus}
    durations: list[float] = []

    for job in jobs:
        by_status[job.status.value] += 1
        if job.duration_s is not None:
            durations.append(job.duration_s)

    avg_duration = round(sum(durations) / len(durations), 2) if durations else 0.0
    failure_rate = round((by_status[JobStatus.FAILED.value] / total), 2) if total else 0.0
    return Stats(
        total=total,
        by_status=by_status,
        avg_duration_s=avg_duration,
        failure_rate=failure_rate,
    )

