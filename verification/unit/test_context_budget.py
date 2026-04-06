from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT, run_command


sys.path.insert(0, str(REPO_ROOT / "scripts"))

from context_budget import ModifierContext, infer_artifact_type, score_bundle  # noqa: E402


PYTHON = sys.executable
WORK_SCRIPT = REPO_ROOT / "scripts" / "work.py"


def run_work_command(*args: str) -> tuple[int, str, str]:
    result = run_command([PYTHON, str(WORK_SCRIPT), *args], cwd=REPO_ROOT, timeout=240)
    return result.returncode, result.stdout, result.stderr


class ContextBudgetTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = REPO_ROOT
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write_temp_file(self, relative_path: str, content: str) -> Path:
        path = self.temp_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class TestArtifactTypeInference(ContextBudgetTestCase):
    def test_manifest_path(self) -> None:
        self.assertEqual(infer_artifact_type("manifests/cli-python.yaml"), "manifest")

    def test_doctrine_path(self) -> None:
        self.assertEqual(infer_artifact_type("context/doctrine/core-principles.md"), "doctrine")

    def test_workflow_path(self) -> None:
        self.assertEqual(infer_artifact_type("context/workflows/add-api-endpoint.md"), "workflow")

    def test_stack_pack_path(self) -> None:
        self.assertEqual(infer_artifact_type("context/stacks/python-fastapi-uv-ruff-orjson-polars.md"), "stack_pack")

    def test_archetype_path(self) -> None:
        self.assertEqual(infer_artifact_type("context/archetypes/backend-api-service.md"), "archetype_pack")

    def test_anchor_agent_md(self) -> None:
        self.assertEqual(infer_artifact_type("AGENT.md"), "anchor")

    def test_deployment_doctrine(self) -> None:
        self.assertEqual(
            infer_artifact_type("context/doctrine/deployment-philosophy-dokku.md"),
            "deployment_doctrine",
        )

    def test_example_large(self) -> None:
        path = self._write_temp_file("examples/canonical-api/oversized-example.py", "x" * 9000)
        self.assertEqual(infer_artifact_type(str(path)), "large_example")


class TestArtifactScoring(ContextBudgetTestCase):
    def test_doctrine_base_cost(self) -> None:
        bundle_score, _profile, _violations = score_bundle(
            ["context/doctrine/core-principles.md"],
            self.repo_root,
        )
        self.assertEqual(bundle_score.artifacts[0].base_cost, 3)

    def test_manifest_base_cost(self) -> None:
        bundle_score, _profile, _violations = score_bundle(["manifests/cli-python.yaml"], self.repo_root)
        self.assertEqual(bundle_score.artifacts[0].base_cost, 2)

    def test_size_cost_zero_small_file(self) -> None:
        path = self._write_temp_file("notes/small.md", "small file\n")
        bundle_score, _profile, _violations = score_bundle([str(path)], self.repo_root)
        self.assertEqual(bundle_score.artifacts[0].size_cost, 0)

    def test_size_cost_nonzero_large_file(self) -> None:
        path = self._write_temp_file("notes/large.md", "x" * 5000)
        bundle_score, _profile, _violations = score_bundle([str(path)], self.repo_root)
        self.assertGreater(bundle_score.artifacts[0].size_cost, 0)

    def test_direct_match_discount_applied(self) -> None:
        bundle_score, _profile, _violations = score_bundle(
            ["context/workflows/add-api-endpoint.md"],
            self.repo_root,
            ctx=ModifierContext(active_workflow="add-api-endpoint"),
        )
        self.assertEqual(bundle_score.artifacts[0].modifier_cost, -1)

    def test_no_modifiers_without_context(self) -> None:
        bundle_score, _profile, _violations = score_bundle(
            ["context/workflows/add-api-endpoint.md"],
            self.repo_root,
        )
        self.assertEqual(bundle_score.artifacts[0].modifier_cost, 0)

    def test_deployment_without_trigger_penalty(self) -> None:
        bundle_score, _profile, _violations = score_bundle(
            ["context/doctrine/deployment-philosophy-dokku.md"],
            self.repo_root,
            ctx=ModifierContext(),
        )
        self.assertEqual(bundle_score.artifacts[0].modifier_cost, 4)
        self.assertIn("deployment without trigger", bundle_score.artifacts[0].modifier_notes)


class TestBundleScoring(ContextBudgetTestCase):
    def test_empty_bundle(self) -> None:
        bundle_score, _profile, _violations = score_bundle([], self.repo_root)
        self.assertEqual(bundle_score.total, 0)

    def test_single_file_bundle(self) -> None:
        bundle_score, _profile, _violations = score_bundle(["context/doctrine/core-principles.md"], self.repo_root)
        artifact = bundle_score.artifacts[0]
        self.assertEqual(bundle_score.total, artifact.base_cost + artifact.size_cost)

    def test_diversity_penalty_applied(self) -> None:
        bundle_score, _profile, _violations = score_bundle(
            [
                "context/stacks/python-fastapi-uv-ruff-orjson-polars.md",
                "context/doctrine/deployment-philosophy-dokku.md",
                "verification/scripts/test_repo_scripts.py",
                "context/doctrine/search-sort-scroll-layout.md",
                "context/SESSION.md",
                "README.md",
            ],
            self.repo_root,
        )
        self.assertGreater(bundle_score.diversity_penalty, 0)

    def test_diversity_penalty_absent(self) -> None:
        bundle_score, _profile, _violations = score_bundle(
            ["AGENT.md", "README.md", "PLAN.md"],
            self.repo_root,
        )
        self.assertEqual(bundle_score.diversity_penalty, 0)

    def test_profile_selection_tiny(self) -> None:
        _bundle_score, profile, _violations = score_bundle(["AGENT.md", "README.md"], self.repo_root)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "tiny")

    def test_profile_selection_medium(self) -> None:
        _bundle_score, profile, _violations = score_bundle(
            [
                "AGENT.md",
                "context/doctrine/core-principles.md",
                "context/workflows/add-api-endpoint.md",
                "context/stacks/python-fastapi-uv-ruff-orjson-polars.md",
                "context/archetypes/backend-api-service.md",
            ],
            self.repo_root,
        )
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, "medium")

    def test_cap_violation_reported(self) -> None:
        _bundle_score, _profile, cap_violations = score_bundle(
            [
                "context/stacks/python-fastapi-uv-ruff-orjson-polars.md",
                "context/stacks/typescript-hono-bun.md",
                "context/stacks/go-echo.md",
                "context/stacks/elixir-phoenix.md",
            ],
            self.repo_root,
        )
        self.assertTrue(cap_violations)


class TestBudgetReportCommand(ContextBudgetTestCase):
    def test_budget_report_requires_bundle(self) -> None:
        code, stdout, stderr = run_work_command("budget-report")
        self.assertEqual(code, 1)
        self.assertIn("usage:", stdout or stderr)

    def test_budget_report_produces_output(self) -> None:
        code, stdout, stderr = run_work_command(
            "budget-report",
            "--bundle",
            "AGENT.md",
            "README.md",
            "context/doctrine/core-principles.md",
        )
        self.assertEqual(code, 0, stderr)
        self.assertIn("Budget Report", stdout)
        self.assertIn("Bundle Summary", stdout)
        self.assertIn("Profile Fit", stdout)

    def test_budget_report_json_flag(self) -> None:
        code, stdout, stderr = run_work_command("budget-report", "--bundle", "AGENT.md", "--json")
        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertIn("bundle_cost", payload)

    def test_budget_report_missing_file_warns(self) -> None:
        code, stdout, stderr = run_work_command("budget-report", "--bundle", "missing-file-does-not-exist.md")
        self.assertEqual(code, 0, stderr)
        self.assertIn("Warning:", stdout)


if __name__ == "__main__":
    unittest.main()
