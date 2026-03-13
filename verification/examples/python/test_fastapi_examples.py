from __future__ import annotations

import ast
import asyncio
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT, docker_enabled, free_tcp_port, run_command, wait_for_http_json
from verification.scenarios.fastapi_min_app.harness import load_example_module, run_fastapi_summary_scenario


EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/fastapi-endpoint-example.py"
SMOKE_TEST_PATH = REPO_ROOT / "examples/canonical-smoke-tests/fastapi-smoke-test-example.py"
INTEGRATION_TEST_PATH = REPO_ROOT / "examples/canonical-integration-tests/fastapi-db-integration-test-example.py"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/fastapi-example"


class FastAPIExampleTests(unittest.TestCase):
    def test_fastapi_example_parses(self) -> None:
        ast.parse(EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_fastapi_example_imports_with_stubs(self) -> None:
        module = load_example_module()
        self.assertTrue(hasattr(module, "router"))
        self.assertTrue(hasattr(module, "ReportService"))

    def test_fastapi_route_mount_and_response_shape(self) -> None:
        result = asyncio.run(run_fastapi_summary_scenario())
        self.assertIn("/reports/summary", result["routes"])
        self.assertIn("/reports/summary", result["mounted_routes"])
        self.assertEqual(result["response"][0]["report_id"], "daily-signups")
        self.assertLessEqual(result["response"][0]["error_rate"], 1.0)
        self.assertEqual(result["response"][-1]["error_rate"], 0.0)

    def test_related_fastapi_examples_parse(self) -> None:
        for path in (SMOKE_TEST_PATH, INTEGRATION_TEST_PATH):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"))

    def test_fastapi_runtime_container(self) -> None:
        if not docker_enabled():
            self.skipTest("Docker smoke checks require VERIFY_DOCKER=1 and docker")

        tag = f"agent-context-fastapi:{free_tcp_port()}"
        build = run_command(["docker", "build", "-t", tag, "."], cwd=RUNTIME_DIR, timeout=300)
        self.assertEqual(build.returncode, 0, build.stderr or build.stdout)

        port = free_tcp_port()
        run = run_command(
            ["docker", "run", "--rm", "-d", "-p", f"{port}:8000", tag],
            cwd=RUNTIME_DIR,
            timeout=120,
        )
        self.assertEqual(run.returncode, 0, run.stderr or run.stdout)
        container_id = run.stdout.strip()
        try:
            status, payload = wait_for_http_json(f"http://127.0.0.1:{port}/healthz", timeout=25.0)
            self.assertEqual(status, 200)
            self.assertEqual(payload, {"status": "ok", "service": "fastapi-example"})
        finally:
            run_command(["docker", "rm", "-f", container_id], timeout=60)


if __name__ == "__main__":
    unittest.main()
