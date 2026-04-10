from __future__ import annotations

import copy
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


def load_events(events_path: Path) -> list[dict]:
    with events_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_jobs(jobs_path: Path) -> list[dict]:
    with jobs_path.open(encoding="utf-8") as handle:
        return json.load(handle)


def parse_delta(ts_new: str, ts_old: str) -> float:
    """Return seconds between two ISO8601 timestamps."""
    new_dt = datetime.fromisoformat(ts_new.replace("Z", "+00:00")).astimezone(timezone.utc)
    old_dt = datetime.fromisoformat(ts_old.replace("Z", "+00:00")).astimezone(timezone.utc)
    return (new_dt - old_dt).total_seconds()


def sort_by_timestamp(events: list[dict]) -> list[dict]:
    return sorted(events, key=lambda event: (event["timestamp"], event.get("event_id", "")))


def replay_events(
    events_path: Path,
    speed_factor: float = 1.0,
    max_events: int | None = None,
) -> Iterator[dict]:
    """
    Yield events in timestamp order.

    `speed_factor=1.0` replays at real time, `10.0` is 10x faster, and `0.0`
    disables sleeping entirely.
    """
    events = sort_by_timestamp(load_events(events_path))
    if max_events is not None:
        events = events[:max_events]

    previous_timestamp: str | None = None
    for event in events:
        if previous_timestamp is not None and speed_factor > 0:
            delay_s = parse_delta(event["timestamp"], previous_timestamp) / speed_factor
            if delay_s > 0:
                time.sleep(delay_s)
        yield event
        previous_timestamp = event["timestamp"]


def _duration_from_start(started_at: str | None, current_timestamp: str) -> float | None:
    if not started_at:
        return None
    return max(parse_delta(current_timestamp, started_at), 0.0)


def _append_output_line(job: dict, line: str) -> None:
    output_lines = job.get("output_lines")
    if not isinstance(output_lines, list):
        output_lines = []
        job["output_lines"] = output_lines
    output_lines.append(line)


def _apply_event(job: dict, event: dict) -> None:
    event_type = event["event_type"]
    timestamp = event["timestamp"]
    message = event.get("message", "")

    if event_type == "job_queued":
        if job.get("status") not in {"running", "done", "failed"}:
            job["status"] = "pending"
            job["started_at"] = None
            job["duration_s"] = None
    elif event_type == "job_started":
        job["status"] = "running"
        job["started_at"] = job.get("started_at") or timestamp
        job["duration_s"] = None
    elif event_type == "job_completed":
        job["status"] = "done"
        job["started_at"] = job.get("started_at") or timestamp
        job["duration_s"] = _duration_from_start(job.get("started_at"), timestamp)
    elif event_type == "job_failed":
        job["status"] = "failed"
        job["started_at"] = job.get("started_at") or timestamp
        job["duration_s"] = _duration_from_start(job.get("started_at"), timestamp)

    if message:
        _append_output_line(job, message)


def replay_to_state(
    events_path: Path,
    jobs_path: Path,
    up_to_event: int | None = None,
) -> list[dict]:
    """
    Apply events to a job list up to the Nth event and return the resulting state.
    """
    jobs = copy.deepcopy(load_jobs(jobs_path))
    jobs_by_id = {job["id"]: job for job in jobs}
    events = sort_by_timestamp(load_events(events_path))
    if up_to_event is not None:
        events = events[:up_to_event]

    for event in events:
        job = jobs_by_id.get(event["job_id"])
        if job is None:
            continue
        _apply_event(job, event)

    return jobs
