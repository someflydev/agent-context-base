from __future__ import annotations

import os
import time
import urllib.error
import urllib.request
import unittest
from pathlib import Path

from verification.helpers import (
    REPO_ROOT,
    command_available,
    docker_enabled,
    free_tcp_port,
    run_command,
    wait_for_http_json,
)


RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/scala-tapir-http4s-zio-example"


def wait_for_http_text(url: str, *, timeout: float = 20.0) -> tuple[int, str]:
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


def native_smoke_check() -> None:
    if not command_available("sbt"):
        raise unittest.SkipTest("sbt is not available")

    tmp_root = Path("/tmp/agent-context-scala")
    env = {
        "COURSIER_CACHE": str(tmp_root / "coursier-cache"),
        "SBT_OPTS": (
            f"-Dsbt.boot.directory={tmp_root / 'boot'} "
            f"-Dsbt.global.base={tmp_root / 'global'} "
            f"-Dsbt.ivy.home={tmp_root / 'ivy2'} "
            "-Dsbt.log.noformat=true"
        ),
    }
    result = run_command(["sbt", "compile"], cwd=RUNTIME_DIR, env=env, timeout=900)
    if result.returncode != 0:
        raise AssertionError(result.stderr.strip() or result.stdout.strip())


def docker_smoke_check() -> dict[str, object]:
    if not docker_enabled():
        raise unittest.SkipTest("Docker smoke checks require VERIFY_DOCKER=1 and docker")

    tag = f"agent-context-scala-tapir-http4s-zio:{free_tcp_port()}"
    build = run_command(["docker", "build", "-t", tag, "."], cwd=RUNTIME_DIR, timeout=1200)
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
        health_status, health_payload = wait_for_http_json(f"http://127.0.0.1:{port}/healthz", timeout=75.0)
        api_status, api_payload = wait_for_http_json(
            f"http://127.0.0.1:{port}/api/reports/acme",
            timeout=30.0,
        )
        data_status, data_payload = wait_for_http_json(
            f"http://127.0.0.1:{port}/data/chart/signups",
            timeout=30.0,
        )
        fragment_status, fragment_payload = wait_for_http_text(
            f"http://127.0.0.1:{port}/fragments/report-card/acme",
            timeout=30.0,
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
