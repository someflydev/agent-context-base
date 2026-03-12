from __future__ import annotations

import os
import subprocess
from pathlib import Path

import psycopg
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import create_app


COMPOSE_FILE = Path("docker-compose.test.yml")
TEST_DB_SERVICE = "postgres-test"


def compose(*args: str) -> None:
    subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), *args],
        check=True,
    )


@pytest.fixture(scope="session", autouse=True)
def isolated_test_stack() -> None:
    compose("up", "-d", TEST_DB_SERVICE)
    try:
        yield
    finally:
        compose("down", "-v")


@pytest.fixture(autouse=True)
def reset_test_db(isolated_test_stack: None) -> None:
    subprocess.run(
        ["uv", "run", "python", "scripts/reset_test_db.py", "--compose-file", str(COMPOSE_FILE)],
        check=True,
    )
    subprocess.run(
        ["uv", "run", "python", "scripts/seed_test_db.py", "--compose-file", str(COMPOSE_FILE)],
        check=True,
    )


@pytest.mark.anyio
async def test_create_report_persists_to_isolated_postgres(reset_test_db: None) -> None:
    app = create_app()

    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.post(
                "/reports",
                json={"tenant_id": "acme", "report_id": "daily-signups", "total_events": 42},
            )

    assert response.status_code == 201

    with psycopg.connect(os.environ["TEST_DATABASE_URL"]) as connection:
        row = connection.execute(
            """
            select tenant_id, report_id, total_events
            from report_runs
            where report_id = %s
            """,
            ("daily-signups",),
        ).fetchone()

    assert row == ("acme", "daily-signups", 42)

