from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
GO_DIR = REPO_ROOT / "examples" / "canonical-faker" / "go"
GO_ENV = {
    **os.environ,
    "GOCACHE": "/tmp/go-build",
    "GOMODCACHE": "/tmp/go-mod-cache",
}
BASE_TIME = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


class TestGoFakerExample(unittest.TestCase):
    def test_go_mod_exists(self) -> None:
        go_mod = GO_DIR / "go.mod"
        self.assertTrue(go_mod.exists())
        text = go_mod.read_text(encoding="utf-8")
        self.assertIn("gofakeit", text)
        self.assertIn("go-faker", text)

    def test_types_defined(self) -> None:
        types_go = GO_DIR / "internal" / "domain" / "types.go"
        self.assertTrue(types_go.exists())
        text = types_go.read_text(encoding="utf-8")
        self.assertIn("Organization", text)
        self.assertIn("AuditEvent", text)
        self.assertIn('json:"', text)

    def test_struct_tag_contrast_documented(self) -> None:
        struct_tag = GO_DIR / "internal" / "pipeline" / "struct_tag.go"
        self.assertTrue(struct_tag.exists())
        text = struct_tag.read_text(encoding="utf-8").lower()
        self.assertTrue(
            "relational graph integrity" in text or "orchestration layer" in text
        )

    def test_cli_exists(self) -> None:
        cli = GO_DIR / "cmd" / "generate" / "main.go"
        self.assertTrue(cli.exists())
        text = cli.read_text(encoding="utf-8")
        self.assertIn("flag.String", text)
        self.assertIn("profile", text)

    def test_go_build_if_available(self) -> None:
        if shutil.which("go") is None:
            self.skipTest("go is not installed")
        subprocess.run(["go", "build", "./..."], cwd=GO_DIR, check=True, env=GO_ENV)

    def test_go_smoke_if_available(self) -> None:
        if shutil.which("go") is None:
            self.skipTest("go is not installed")
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                ["go", "run", "./cmd/generate/", "-profile", "smoke", "-output", tmpdir],
                cwd=GO_DIR,
                check=True,
                env=GO_ENV,
            )
            self.assertTrue((Path(tmpdir) / "smoke" / "organizations.jsonl").exists())
            subprocess.run(
                [
                    "python3",
                    "../domain/validate_output.py",
                    "--input-dir",
                    str(Path(tmpdir) / "smoke"),
                ],
                cwd=GO_DIR,
                check=True,
            )
            invitations_path = Path(tmpdir) / "smoke" / "invitations.jsonl"
            if invitations_path.exists():
                for line in invitations_path.read_text(encoding="utf-8").splitlines():
                    invitation = json.loads(line)
                    expires_at = datetime.fromisoformat(
                        invitation["expires_at"].replace("Z", "+00:00")
                    )
                    self.assertGreater(expires_at, BASE_TIME)
                    self.assertLessEqual(
                        expires_at, BASE_TIME + timedelta(days=30)
                    )

    def test_struct_tag_pipeline_is_seed_deterministic_if_available(self) -> None:
        if shutil.which("go") is None:
            self.skipTest("go is not installed")
        with tempfile.TemporaryDirectory() as tmpdir:
            first_output = Path(tmpdir) / "first"
            second_output = Path(tmpdir) / "second"
            for target in (first_output, second_output):
                subprocess.run(
                    [
                        "go",
                        "run",
                        "./cmd/generate/",
                        "-profile",
                        "smoke",
                        "-pipeline",
                        "structtag",
                        "-output",
                        str(target),
                    ],
                    cwd=GO_DIR,
                    check=True,
                    env=GO_ENV,
                )
            for name in (
                "organizations.jsonl",
                "users.jsonl",
                "memberships.jsonl",
                "projects.jsonl",
                "audit_events.jsonl",
                "api_keys.jsonl",
                "invitations.jsonl",
                "smoke-report.json",
            ):
                self.assertEqual(
                    (first_output / "smoke" / name).read_text(encoding="utf-8"),
                    (second_output / "smoke" / name).read_text(encoding="utf-8"),
                )


if __name__ == "__main__":
    unittest.main()
