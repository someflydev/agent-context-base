from __future__ import annotations

import time
import urllib.error
import urllib.request
import unittest

from verification.helpers import REPO_ROOT, docker_enabled, free_tcp_port, run_command, wait_for_http_json


RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/ocaml-dream-caqti-tyxml-example"


def wait_for_http_text(url: str, *, timeout: float = 30.0) -> tuple[int, str]:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2.0) as response:
                return response.status, response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            time.sleep(0.25)
    raise AssertionError(f"timed out waiting for {url}: {last_error}")


def docker_smoke_check() -> dict[str, object]:
    if not docker_enabled():
        raise unittest.SkipTest("Docker smoke checks require VERIFY_DOCKER=1 and docker")

    tag = f"agent-context-ocaml-dream-caqti-tyxml:{free_tcp_port()}"
    build = run_command(["docker", "build", "-t", tag, "."], cwd=RUNTIME_DIR, timeout=1800)
    if build.returncode != 0:
        raise AssertionError(build.stderr.strip() or build.stdout.strip())

    port = free_tcp_port()
    run = run_command(
        ["docker", "run", "--rm", "-d", "-p", f"{port}:8080", tag],
        cwd=RUNTIME_DIR,
        timeout=120,
    )
    if run.returncode != 0:
        raise AssertionError(run.stderr.strip() or run.stdout.strip())

    container_id = run.stdout.strip()
    try:
        health_status, health_payload = wait_for_http_json(f"http://127.0.0.1:{port}/healthz", timeout=90.0)
        api_status, api_payload = wait_for_http_json(
            f"http://127.0.0.1:{port}/api/reports/acme",
            timeout=45.0,
        )
        data_status, data_payload = wait_for_http_json(
            f"http://127.0.0.1:{port}/data/chart/signups",
            timeout=45.0,
        )
        fragment_status, fragment_payload = wait_for_http_text(
            f"http://127.0.0.1:{port}/fragments/report-card/acme",
            timeout=45.0,
        )
        return {
            "health_status": health_status,
            "health_payload": health_payload,
            "api_status": api_status,
            "api_payload": api_payload,
            "data_status": data_status,
            "data_payload": data_payload,
            "fragment_status": fragment_status,
            "fragment_payload": fragment_payload,
        }
    finally:
        run_command(["docker", "rm", "-f", container_id], timeout=60)
