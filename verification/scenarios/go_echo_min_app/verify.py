from __future__ import annotations

from pathlib import Path

from verification.helpers import (
    REPO_ROOT,
    command_available,
    docker_enabled,
    free_tcp_port,
    run_command,
    wait_for_http_json,
)


RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/go-echo-example"


def native_smoke_check() -> None:
    if not command_available("go"):
        raise unittest.SkipTest("go is not available")
    result = run_command(["go", "build", "."], cwd=RUNTIME_DIR, timeout=180)
    if result.returncode != 0:
        raise AssertionError(result.stderr.strip() or result.stdout.strip())


def docker_smoke_check() -> dict[str, object]:
    if not docker_enabled():
        raise unittest.SkipTest("Docker smoke checks require VERIFY_DOCKER=1 and docker")

    tag = f"agent-context-go-echo:{free_tcp_port()}"
    build = run_command(["docker", "build", "-t", tag, "."], cwd=RUNTIME_DIR, timeout=300)
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
        status, payload = wait_for_http_json(f"http://127.0.0.1:{port}/healthz", timeout=25.0)
        return {"status": status, "payload": payload}
    finally:
        run_command(["docker", "rm", "-f", container_id], timeout=60)


import unittest  # noqa: E402  # keep late so SkipTest is available without polluting module constants
