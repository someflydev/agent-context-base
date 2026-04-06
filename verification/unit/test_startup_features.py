from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT, run_command


PYTHON = sys.executable
WORK_SCRIPT = REPO_ROOT / "scripts" / "work.py"
PROFILE_RULES_PATH = REPO_ROOT / "context" / "acb" / "profile-rules.json"


def run_work_command(*args: str, cwd: Path) -> tuple[int, str, str]:
    result = run_command([PYTHON, str(cwd / "scripts" / "work.py"), *args], cwd=cwd, timeout=240)
    return result.returncode, result.stdout, result.stderr


class StartupFeatureRepoTestCase(unittest.TestCase):
    def _run_checked_command(self, args: list[str], cwd: Path) -> str:
        result = run_command(args, cwd=cwd, timeout=240)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def _write_file(self, repo: Path, relative_path: str, content: str) -> None:
        path = repo / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _create_repo(self, startup_features: dict[str, bool] | None = None) -> Path:
        repo = Path(tempfile.mkdtemp())
        self._run_checked_command(["git", "init"], cwd=repo)
        self._run_checked_command(["git", "config", "user.name", "ACB Test"], cwd=repo)
        self._run_checked_command(["git", "config", "user.email", "acb-test@example.com"], cwd=repo)
        self._write_file(repo, "scripts/work.py", WORK_SCRIPT.read_text(encoding="utf-8"))
        self._write_file(repo, "README.md", "# Temp Repo\n")
        self._write_file(repo, "PLAN.md", "# PLAN.md\n\n## Active Phase\n- Startup features\n")
        self._write_file(repo, "context/TASK.md", "# TASK.md\n\n## Current Slice\n- Verify briefing tool availability.\n")
        self._write_file(repo, "context/SESSION.md", "# SESSION.md\n\n## Next Safe Step\n- Run work.py resume.\n")
        self._write_file(repo, "context/MEMORY.md", "# MEMORY.md\n\n## Durable Rules\n- Keep startup context visible.\n")
        if startup_features is not None:
            self._write_file(
                repo,
                ".acb/profile/selection.json",
                json.dumps({"startup_features": startup_features}, indent=2) + "\n",
            )
        return repo


class TestStartupFeaturesConfig(unittest.TestCase):
    def test_profile_rules_has_startup_features(self) -> None:
        payload = json.loads(PROFILE_RULES_PATH.read_text(encoding="utf-8"))
        self.assertIn("startup_features", payload)
        self.assertEqual(
            set(payload["startup_features"]),
            {"budget_report_enabled", "startup_trace_enabled", "route_check_enabled"},
        )

    def test_startup_features_defaults_false(self) -> None:
        payload = json.loads(PROFILE_RULES_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["startup_features"],
            {
                "budget_report_enabled": False,
                "startup_trace_enabled": False,
                "route_check_enabled": False,
            },
        )

    def test_session_briefing_shows_context_tools(self) -> None:
        result = run_command([PYTHON, str(WORK_SCRIPT), "resume"], cwd=REPO_ROOT, timeout=240)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Context Tools:", result.stdout)
        self.assertIn("budget-report:       available", result.stdout)


class TestDerivedRepoToggleability(StartupFeatureRepoTestCase):
    def test_selection_json_propagates_startup_features(self) -> None:
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from acb_payload import build_payload, load_available_manifests  # noqa: E402

        files, _metadata = build_payload(
            archetype="backend-api-service",
            primary_stack="python-fastapi-uv-ruff-orjson-polars",
            selected_manifests=["backend-api-fastapi-polars"],
            manifests=load_available_manifests(),
            support_services=["postgres"],
            prompt_first=True,
            dokku=False,
        )
        selection = json.loads(files[".acb/profile/selection.json"])
        self.assertEqual(
            selection["startup_features"],
            {
                "budget_report_enabled": False,
                "startup_trace_enabled": False,
                "route_check_enabled": False,
            },
        )

    def test_briefing_reads_startup_features_from_selection_json(self) -> None:
        repo = self._create_repo(
            {
                "budget_report_enabled": True,
                "startup_trace_enabled": False,
                "route_check_enabled": True,
            }
        )
        code, stdout, stderr = run_work_command("resume", cwd=repo)
        self.assertEqual(code, 0, stderr)
        self.assertIn("Context Tools:", stdout)
        self.assertIn("budget-report:       available", stdout)
        self.assertIn("startup-trace:       n/a (disabled)", stdout)
        self.assertIn("route-check:         available", stdout)
