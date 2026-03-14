from __future__ import annotations

import os
import unittest

from verification.helpers import REPO_ROOT, run_command
from verification.scenarios.rust_axum_min_app.verify import docker_smoke_check, native_smoke_check


EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/rust-axum-route-example.rs"
DATA_ACQUISITION_EXAMPLE_PATH = REPO_ROOT / "examples/canonical-data-acquisition/rust-axum-source-sync-example.rs"
RUNTIME_DIR = REPO_ROOT / "examples/canonical-api/rust-axum-example"


class RustAxumExampleTests(unittest.TestCase):
    def test_route_source_contains_expected_surface(self) -> None:
        text = EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn('route("/tenants/:tenant_id/reports", get(list_reports))', text)
        self.assertIn("Json(reports)", text)

    def test_runtime_bundle_files_exist(self) -> None:
        for relative in ("Cargo.toml", "Dockerfile", "README.md", "src/main.rs"):
            with self.subTest(relative=relative):
                self.assertTrue((RUNTIME_DIR / relative).exists())

    def test_data_acquisition_example_is_rustfmt_parsable(self) -> None:
        result = run_command(
            ["rustfmt", "--edition", "2021", "--check", DATA_ACQUISITION_EXAMPLE_PATH.as_posix()],
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_data_acquisition_example_contains_expected_sync_markers(self) -> None:
        text = DATA_ACQUISITION_EXAMPLE_PATH.read_text(encoding="utf-8")
        self.assertIn("pub trait SourceAdapter", text)
        self.assertIn("pub async fn archive_raw_capture", text)
        self.assertIn("pub async fn replay_from_archive", text)
        self.assertIn('.route("/sources/github-releases/:owner/:repo/sync", post(run_sync))', text)
        self.assertIn('format!("page-{page}.json")', text)
        self.assertIn("for _attempt in 1..=attempts", text)

    def test_optional_native_rust_build(self) -> None:
        if os.environ.get("VERIFY_HEAVY_NATIVE", "").strip().lower() not in {"1", "true", "yes", "on"}:
            self.skipTest("native Rust build is reserved for heavy verification")
        native_smoke_check()

    def test_optional_docker_rust_runtime(self) -> None:
        payload = docker_smoke_check()
        self.assertEqual(payload["status"], 200)
        self.assertEqual(payload["payload"], {"status": "ok", "service": "rust-axum-example"})


if __name__ == "__main__":
    unittest.main()
