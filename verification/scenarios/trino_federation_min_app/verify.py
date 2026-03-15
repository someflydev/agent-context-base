from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

from verification.helpers import (
    REPO_ROOT,
    docker_enabled,
    free_tcp_port,
    run_command,
)


SCENARIO_DIR = REPO_ROOT / "verification/scenarios/trino_federation_min_app"

# Seed data -------------------------------------------------------------------

_SEED_PG = """
CREATE TABLE IF NOT EXISTS tenants (
    tenant_id   TEXT PRIMARY KEY,
    tenant_name TEXT NOT NULL
);
INSERT INTO tenants (tenant_id, tenant_name) VALUES
    ('acme',   'Acme Corp'),
    ('globex', 'Globex Inc')
ON CONFLICT DO NOTHING;
"""

# mongosh --eval receives a single JS expression; use a semicolon-separated
# block wrapped in quotes so the shell passes it through intact.
_SEED_MONGO = (
    "db = db.getSiblingDB('reporting');"
    "db.request_logs.insertMany(["
    "  { tenant_id: 'acme',   report_id: 'daily-signups',   request_at: new Date(),"
    "    response_status: 200, response_ms: 120, payload_version: 1, row_count: 42 },"
    "  { tenant_id: 'acme',   report_id: 'daily-signups',   request_at: new Date(),"
    "    response_status: 200, response_ms: 145, payload_version: 1, row_count: 38 },"
    "  { tenant_id: 'globex', report_id: 'weekly-revenue',  request_at: new Date(),"
    "    response_status: 200, response_ms: 230, payload_version: 1, row_count: 15 },"
    "  { tenant_id: 'acme',   report_id: 'daily-signups',   request_at: new Date(),"
    "    response_status: 500, response_ms: 12,  payload_version: 1, row_count: 0 },"
    "]);"
)

# Verification query ----------------------------------------------------------
# Simplified from the canonical example: no DATE_TRUNC so the result shape is
# easy to assert without worrying about week-boundary arithmetic.

_FEDERATED_QUERY = """
SELECT
    t.tenant_id,
    t.tenant_name,
    COUNT(*)                                         AS total_requests,
    COUNT(*) FILTER (WHERE e.response_status < 400) AS successful_requests
FROM
    postgresql_prod.public.tenants AS t
    JOIN mongo_events.reporting.request_logs AS e
        ON t.tenant_id = e.tenant_id
GROUP BY
    t.tenant_id,
    t.tenant_name
ORDER BY
    t.tenant_id
"""

# Internal helpers ------------------------------------------------------------


def _compose(
    project: str,
    port: int,
    args: list[str],
    *,
    timeout: int = 120,
) -> Any:
    return run_command(
        [
            "docker", "compose",
            "--project-name", project,
            "--file", str(SCENARIO_DIR / "docker-compose.test.yml"),
        ] + args,
        cwd=SCENARIO_DIR,
        env={"TRINO_PORT": str(port)},
        timeout=timeout,
    )


def _wait_for_postgres(project: str, port: int, *, timeout: float = 60.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = _compose(
            project, port,
            ["exec", "-T", "postgres", "pg_isready", "-U", "trino_read", "-d", "testdb"],
            timeout=10,
        )
        if result.returncode == 0:
            return
        time.sleep(2)
    raise AssertionError("PostgreSQL did not become ready in time")


def _wait_for_mongo(project: str, port: int, *, timeout: float = 60.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = _compose(
            project, port,
            ["exec", "-T", "mongo", "mongosh", "--quiet", "--eval", "db.adminCommand('ping').ok"],
            timeout=10,
        )
        if result.returncode == 0:
            return
        time.sleep(2)
    raise AssertionError("MongoDB did not become ready in time")


def _wait_for_trino(url: str, *, timeout: float = 180.0) -> None:
    """Poll /v1/info until Trino reports starting: false."""
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{url}/v1/info", timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data.get("starting", True):
                    return
        except Exception as exc:
            last_error = exc
        time.sleep(3)
    raise AssertionError(f"Trino did not become ready within {timeout}s: {last_error}")


def _run_trino_query(url: str, sql: str, *, timeout: float = 60.0) -> list[dict[str, Any]]:
    """Submit a Trino query via HTTP API and collect all rows as dicts."""
    req = urllib.request.Request(
        f"{url}/v1/statement",
        data=sql.strip().encode("utf-8"),
        headers={"X-Trino-User": "test", "Content-Type": "text/plain"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    deadline = time.time() + timeout
    rows: list[list[Any]] = []
    columns: list[str] | None = None

    while True:
        if "error" in data:
            raise AssertionError(
                f"Trino query error: {data['error'].get('message', data['error'])}"
            )
        if "columns" in data:
            columns = [col["name"] for col in data["columns"]]
        if "data" in data:
            rows.extend(data["data"])
        next_uri = data.get("nextUri")
        if not next_uri:
            break
        if time.time() > deadline:
            raise TimeoutError("Trino query polling timed out")
        time.sleep(0.5)
        # Retry on transient connection errors; Trino may close the
        # connection while loading connectors on the first query.
        for attempt in range(3):
            try:
                with urllib.request.urlopen(next_uri, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2)

    if not columns:
        return []
    return [dict(zip(columns, row)) for row in rows]


def _warm_up_catalogs(url: str) -> None:
    """Run a trivial query against each catalog to trigger lazy connector init.

    Trino initialises connectors on first use. Running a lightweight query
    before the real federated query prevents the first cross-catalog join from
    hitting the connector during its slow initial load, which can cause the
    HTTP connection to drop.
    """
    for sql in (
        "SHOW CATALOGS",
        "SELECT 1 FROM postgresql_prod.public.tenants LIMIT 1",
        "SELECT 1 FROM mongo_events.reporting.request_logs LIMIT 1",
    ):
        try:
            _run_trino_query(url, sql, timeout=30.0)
        except Exception:
            # Warm-up failures are not fatal; the real query will surface
            # errors with more context.
            pass


# Public entry point ----------------------------------------------------------


def federation_smoke_check() -> list[dict[str, Any]]:
    """
    Start postgres + mongo + trino via docker compose, seed both sources,
    run the federated join query, and return the result rows.

    Raises unittest.SkipTest when VERIFY_DOCKER is not set.
    Raises AssertionError on any failure.
    Always tears down the compose stack on exit.
    """
    if not docker_enabled():
        import unittest
        raise unittest.SkipTest(
            "Trino federation smoke check requires VERIFY_DOCKER=1 and docker"
        )

    port = free_tcp_port()
    project = f"trino-federation-{port}"
    url = f"http://localhost:{port}"

    try:
        up = _compose(project, port, ["up", "-d"], timeout=60)
        if up.returncode != 0:
            raise AssertionError(f"docker compose up failed:\n{up.stderr or up.stdout}")

        _wait_for_postgres(project, port)
        _wait_for_mongo(project, port)
        _wait_for_trino(url)

        seed_pg = _compose(
            project, port,
            ["exec", "-T", "postgres", "psql", "-U", "trino_read", "-d", "testdb", "-c", _SEED_PG],
            timeout=30,
        )
        if seed_pg.returncode != 0:
            raise AssertionError(f"postgres seed failed:\n{seed_pg.stderr or seed_pg.stdout}")

        seed_mongo = _compose(
            project, port,
            ["exec", "-T", "mongo", "mongosh", "--quiet", "--eval", _SEED_MONGO],
            timeout=30,
        )
        if seed_mongo.returncode != 0:
            raise AssertionError(f"mongo seed failed:\n{seed_mongo.stderr or seed_mongo.stdout}")

        _warm_up_catalogs(url)
        return _run_trino_query(url, _FEDERATED_QUERY)

    finally:
        _compose(project, port, ["down", "--volumes", "--remove-orphans"], timeout=60)
