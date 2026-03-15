from __future__ import annotations

from verification.helpers import (
    REPO_ROOT,
    command_available,
    docker_enabled,
    free_tcp_port,
    run_command,
    wait_for_http_json,
)


RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/phoenix-example"


def native_smoke_check() -> None:
    if not command_available("mix"):
        raise unittest.SkipTest("mix is not available")
    deps = run_command(["mix", "deps.get"], cwd=RUNTIME_DIR, timeout=120)
    if deps.returncode != 0:
        raise AssertionError(deps.stderr.strip() or deps.stdout.strip())
    compile_ = run_command(["mix", "compile"], cwd=RUNTIME_DIR, timeout=180)
    if compile_.returncode != 0:
        raise AssertionError(compile_.stderr.strip() or compile_.stdout.strip())


def docker_smoke_check() -> dict[str, object]:
    if not docker_enabled():
        raise unittest.SkipTest("Docker smoke checks require VERIFY_DOCKER=1 and docker")

    tag = f"agent-context-phoenix:{free_tcp_port()}"
    build = run_command(["docker", "build", "-t", tag, "."], cwd=RUNTIME_DIR, timeout=600)
    if build.returncode != 0:
        raise AssertionError(build.stderr.strip() or build.stdout.strip())

    port = free_tcp_port()
    run = run_command(
        ["docker", "run", "--rm", "-d", "-p", f"{port}:4000", tag],
        cwd=RUNTIME_DIR,
        timeout=120,
    )
    if run.returncode != 0:
        raise AssertionError(run.stderr.strip() or run.stdout.strip())

    container_id = run.stdout.strip()
    try:
        status, payload = wait_for_http_json(f"http://127.0.0.1:{port}/healthz", timeout=35.0)
        assert status == 200
        assert payload["status"] == "ok"
        return {"status": status, "payload": payload}
    finally:
        run_command(["docker", "rm", "-f", container_id], timeout=60)


import unittest  # noqa: E402
