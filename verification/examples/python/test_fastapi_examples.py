from __future__ import annotations

import ast
import asyncio
import tempfile
import unittest
import urllib.request
from pathlib import Path

from verification.helpers import (
    REPO_ROOT,
    compat_dataclasses_module,
    docker_enabled,
    fastapi_stub_module,
    free_tcp_port,
    load_python_module,
    orjson_stub_module,
    polars_stub_module,
    run_command,
    wait_for_http_json,
)
from verification.scenarios.fastapi_min_app.harness import load_example_module, run_fastapi_summary_scenario


EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/fastapi-endpoint-example.py"
DATA_ACQUISITION_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-data-acquisition/fastapi-source-sync-example.py"
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

    def test_fastapi_data_acquisition_example_parses(self) -> None:
        ast.parse(DATA_ACQUISITION_EXAMPLE_PATH.read_text(encoding="utf-8"))

    def test_fastapi_data_acquisition_archives_replays_and_retries(self) -> None:
        module = load_python_module(
            DATA_ACQUISITION_EXAMPLE_PATH,
            module_name="canonical_fastapi_source_sync_example",
            stub_modules={
                "dataclasses": compat_dataclasses_module(),
                "fastapi": fastapi_stub_module(),
                "orjson": orjson_stub_module(),
                "polars": polars_stub_module(),
            },
        )

        payload = [
            {
                "id": 102,
                "tag_name": "v1.1.0",
                "name": "January cut",
                "html_url": "https://github.com/octocat/hello-world/releases/tag/v1.1.0",
                "published_at": "2025-01-15T09:30:00Z",
                "draft": False,
            },
            {
                "id": 99,
                "tag_name": "v1.0.0",
                "name": "Initial release",
                "html_url": "https://github.com/octocat/hello-world/releases/tag/v1.0.0",
                "published_at": "2024-12-01T12:00:00Z",
                "draft": False,
            },
        ]

        class StubAdapter:
            def __init__(self) -> None:
                self.calls = 0

            def fetch_release_page(self, _cursor: object) -> object:
                self.calls += 1
                if self.calls == 1:
                    raise module.RetryableFetchError("retry once before archiving")
                return module.FetchResult(
                    body=module.orjson.dumps(payload),
                    fetched_at=module.datetime(2025, 2, 1, 10, 30, tzinfo=module.timezone.utc),
                    status_code=200,
                    content_type="application/json",
                    request_url=(
                        "https://api.github.com/repos/octocat/hello-world/releases?"
                        "per_page=50&page=3"
                    ),
                    checkpoint_token='W/"etag-3"',
                    next_page=4,
                )

        adapter = StubAdapter()
        with tempfile.TemporaryDirectory() as temp_dir:
            service = module.GitHubReleaseSyncService(adapter=adapter, archive_root=Path(temp_dir))
            result = service.sync_release_page(
                module.SyncCursor(
                    owner="octocat",
                    repo="hello-world",
                    page=3,
                    etag='W/"etag-2"',
                    max_attempts=2,
                )
            )

            self.assertEqual(adapter.calls, 2)
            self.assertTrue(result.raw_capture.raw_path.endswith("page-3.json"))
            self.assertTrue(Path(result.raw_capture.raw_path).exists())
            self.assertTrue(Path(result.raw_capture.metadata_path).exists())
            self.assertEqual(result.records[0].canonical_id, "github-releases:octocat/hello-world:102")
            self.assertEqual(result.records[0].provenance.raw_path, result.raw_capture.raw_path)
            self.assertEqual(result.records[0].provenance.checkpoint_token, 'W/"etag-3"')
            self.assertEqual(result.next_cursor.page, 4)

            replayed = service.replay_from_archive(result.raw_capture)
            self.assertEqual(
                [record.canonical_id for record in replayed],
                [record.canonical_id for record in result.records],
            )

            route_paths = [route["path"] for route in module.router.routes]
            self.assertIn("/source-sync/github-releases", route_paths)

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

            chart_status, chart_payload = wait_for_http_json(
                f"http://127.0.0.1:{port}/api/reports/chart?team_in=growth&status_out=archived",
                timeout=25.0,
            )
            self.assertEqual(chart_status, 200)
            self.assertEqual(chart_payload["result_count"], 3)
            self.assertEqual(chart_payload["totals"]["events"], 28)

            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/ui/reports/results?team_in=growth&status_out=archived&region_in=us",
                timeout=5.0,
            ) as response:
                fragment_text = response.read().decode("utf-8")
            self.assertIn('data-result-count="2"', fragment_text)
            self.assertIn('data-report-id="daily-signups"', fragment_text)
        finally:
            run_command(["docker", "rm", "-f", container_id], timeout=60)


if __name__ == "__main__":
    unittest.main()
