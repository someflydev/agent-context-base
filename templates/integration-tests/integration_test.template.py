from __future__ import annotations

import subprocess
from pathlib import Path


COMPOSE_FILE = Path("docker-compose.test.yml")


def compose(*args: str) -> None:
    subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), *args],
        check=True,
    )


def test_real_boundary_round_trip() -> None:
    compose("up", "-d")
    try:
        # Replace this with one real write plus one real read assertion.
        assert True
    finally:
        compose("down", "-v")

