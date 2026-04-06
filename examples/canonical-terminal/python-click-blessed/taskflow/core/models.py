from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


def parse_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def format_timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass(slots=True)
class Job:
    id: str
    name: str
    status: JobStatus
    started_at: datetime | None
    duration_s: float | None
    tags: list[str]
    output_lines: list[str]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Job":
        return cls(
            id=payload["id"],
            name=payload["name"],
            status=JobStatus(payload["status"]),
            started_at=parse_timestamp(payload.get("started_at")),
            duration_s=payload.get("duration_s"),
            tags=list(payload.get("tags", [])),
            output_lines=list(payload.get("output_lines", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "started_at": format_timestamp(self.started_at),
            "duration_s": self.duration_s,
            "tags": self.tags,
            "output_lines": self.output_lines,
        }


@dataclass(slots=True)
class Event:
    event_id: str
    job_id: str
    event_type: str
    timestamp: datetime
    message: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "Event":
        timestamp = parse_timestamp(payload["timestamp"])
        if timestamp is None:
            raise ValueError("event timestamp cannot be null")
        return cls(
            event_id=payload["event_id"],
            job_id=payload["job_id"],
            event_type=payload["event_type"],
            timestamp=timestamp,
            message=payload["message"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "job_id": self.job_id,
            "event_type": self.event_type,
            "timestamp": format_timestamp(self.timestamp),
            "message": self.message,
        }


@dataclass(slots=True)
class Stats:
    total: int
    by_status: dict[str, int]
    avg_duration_s: float
    failure_rate: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "by_status": self.by_status,
            "avg_duration_s": self.avg_duration_s,
            "failure_rate": self.failure_rate,
        }

