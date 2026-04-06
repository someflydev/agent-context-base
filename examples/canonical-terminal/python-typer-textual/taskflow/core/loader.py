from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from taskflow.core.models import Event, Job


class FixtureError(RuntimeError):
    """Raised when fixture data cannot be loaded."""


def default_fixtures_path() -> Path:
    env_path = os.environ.get("TASKFLOW_FIXTURES_PATH")
    if env_path:
        return Path(env_path).expanduser().resolve()

    example_root = Path(__file__).resolve().parents[3]
    candidate = example_root / "fixtures"
    if candidate.exists():
        return candidate.resolve()

    repo_root = Path(__file__).resolve().parents[5]
    fallback = repo_root / "examples" / "canonical-terminal" / "fixtures"
    return fallback.resolve()


def _load_json(fixtures_path: Path, filename: str) -> Any:
    fixture_dir = fixtures_path.expanduser().resolve()
    target = fixture_dir / filename
    if not fixture_dir.exists():
        raise FixtureError(f"fixtures path does not exist: {fixture_dir}")
    if not target.exists():
        raise FixtureError(f"missing fixture file: {target}")
    return json.loads(target.read_text(encoding="utf-8"))


def load_jobs(fixtures_path: Path) -> list[Job]:
    return [Job.from_dict(item) for item in _load_json(fixtures_path, "jobs.json")]


def load_events(fixtures_path: Path) -> list[Event]:
    events = [Event.from_dict(item) for item in _load_json(fixtures_path, "events.json")]
    return sorted(events, key=lambda event: event.timestamp)


def load_config(fixtures_path: Path) -> dict[str, Any]:
    return _load_json(fixtures_path, "config.json")
