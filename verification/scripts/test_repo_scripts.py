from __future__ import annotations

import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT, run_command


PYTHON = sys.executable
SCRIPTS_DIR = REPO_ROOT / "scripts"


def run_script(*args: str, cwd: Path | None = None) -> tuple[int, str, str]:
    result = run_command([PYTHON, *args], cwd=cwd or REPO_ROOT, timeout=240)
    return result.returncode, result.stdout, result.stderr


class RepoScriptTests(unittest.TestCase):
    def test_new_repo_prints_real_derived_prompt_text(self) -> None:
        code, stdout, stderr = run_script(
            str(SCRIPTS_DIR / "new_repo.py"),
            "--derived-example",
            "ingestion-normalization-core",
            "--dry-run",
        )
        self.assertEqual(code, 0, stderr)
        self.assertIn("Build an end-to-end data ingestion and normalization core", stdout)
        self.assertNotIn("block-scalar-content", stdout)

    def test_new_repo_generates_leaf_derived_repo_under_parent_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            target = parent / "ingestion-normalization-core"
            code, stdout, stderr = run_script(
                str(SCRIPTS_DIR / "new_repo.py"),
                "--derived-example",
                "ingestion-normalization-core",
                "--target-dir",
                str(parent),
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Generated starter repo", stdout)
            self.assertTrue(target.exists())
            self.assertTrue((target / ".prompts/PROMPT_01.txt").exists())
            self.assertTrue((target / ".prompts/PROMPT_04.txt").exists())
            self.assertTrue((target / "manifests/project-profile.yaml").exists())
            self.assertTrue((target / "manifests/base/prompt-first-meta-repo.yaml").exists())

    def test_new_repo_vendors_selected_manifests_into_generated_repo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "analytics-api"
            code, stdout, stderr = run_script(
                str(SCRIPTS_DIR / "new_repo.py"),
                "analytics-api",
                "--target-dir",
                str(target),
                "--archetype",
                "backend-api-service",
                "--primary-stack",
                "python-fastapi-uv-ruff-orjson-polars",
                "--manifest",
                "backend-api-fastapi-polars",
                "--manifest",
                "data-acquisition-service",
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Generated starter repo", stdout)
            profile = (target / "manifests/project-profile.yaml").read_text(encoding="utf-8")
            self.assertTrue((target / "manifests/base/backend-api-fastapi-polars.yaml").exists())
            self.assertTrue((target / "manifests/base/data-acquisition-service.yaml").exists())
            self.assertIn("vendored_base_manifests_dir: manifests/base", profile)
            self.assertIn("- manifests/base/backend-api-fastapi-polars.yaml", profile)
            self.assertIn("- manifests/base/data-acquisition-service.yaml", profile)

    def test_new_repo_generates_team_a_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            code, _, stderr = run_script(
                str(SCRIPTS_DIR / "new_repo.py"),
                "--derived-example",
                "team-a",
                "--target-dir",
                str(parent),
            )
            self.assertEqual(code, 0, stderr)
            for child in (
                "ingestion-normalization-core",
                "analytics-lake-deployment",
                "ml-gateway-intelligence",
                "operator-surface",
            ):
                self.assertTrue((parent / child).exists(), child)

    def test_new_repo_dry_run_for_team_a_lists_all_child_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir).resolve()
            code, stdout, stderr = run_script(
                str(SCRIPTS_DIR / "new_repo.py"),
                "--derived-example",
                "team-a",
                "--target-dir",
                str(parent),
                "--dry-run",
            )
            self.assertEqual(code, 0, stderr)
            for child in (
                "ingestion-normalization-core",
                "analytics-lake-deployment",
                "ml-gateway-intelligence",
                "operator-surface",
            ):
                self.assertIn(str(parent / child), stdout)

    def test_new_repo_derived_target_dir_exact_path_is_respected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            exact_target = Path(temp_dir) / "custom-derived-path"
            code, _, stderr = run_script(
                str(SCRIPTS_DIR / "new_repo.py"),
                "--derived-example",
                "ingestion-normalization-core",
                "--target-dir",
                str(exact_target),
            )
            self.assertEqual(code, 0, stderr)
            self.assertTrue((exact_target / ".prompts/PROMPT_01.txt").exists())
            self.assertFalse((exact_target / "ingestion-normalization-core").exists())

    def test_new_repo_list_derived_includes_collection_selectors(self) -> None:
        code, stdout, stderr = run_script(str(SCRIPTS_DIR / "new_repo.py"), "--list-derived")
        self.assertEqual(code, 0, stderr)
        self.assertIn("team-a", stdout)
        self.assertIn("team-b", stdout)
        self.assertIn("all-derived", stdout)

    def test_validate_manifests_script_passes(self) -> None:
        code, stdout, stderr = run_script(str(SCRIPTS_DIR / "validate_manifests.py"))
        self.assertEqual(code, 0, stderr)
        self.assertIn("Validated", stdout)

    def test_validate_doc_governance_script_passes(self) -> None:
        code, stdout, stderr = run_script(str(SCRIPTS_DIR / "validate_doc_governance.py"))
        self.assertEqual(code, 0, stderr)
        self.assertIn("Validated markdown links", stdout)

    def test_new_repo_bootstraps_prompt_first_repo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "prompt-kit"
            code, stdout, stderr = run_script(
                str(SCRIPTS_DIR / "new_repo.py"),
                "prompt-kit",
                "--target-dir",
                str(target),
                "--archetype",
                "prompt-first-repo",
                "--primary-stack",
                "prompt-first-repo",
                "--prompt-first",
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Generated starter repo", stdout)
            self.assertTrue((target / ".prompts/001-bootstrap-repo.txt").exists())
            self.assertTrue((target / "AGENT.md").exists())
            self.assertTrue((target / "manifests/base/prompt-first-meta-repo.yaml").exists())
            self.assertFalse((target / "README.md").exists())
            self.assertFalse((target / "docs").exists())

    def test_new_repo_can_opt_into_front_docs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "analytics-api"
            code, stdout, stderr = run_script(
                str(SCRIPTS_DIR / "new_repo.py"),
                "analytics-api",
                "--target-dir",
                str(target),
                "--archetype",
                "backend-api-service",
                "--primary-stack",
                "python-fastapi-uv-ruff-orjson-polars",
                "--include-root-readme",
                "--include-docs-dir",
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Generated starter repo", stdout)
            self.assertTrue((target / "README.md").exists())
            self.assertTrue((target / "docs/repo-purpose.md").exists())
            self.assertTrue((target / "docs/repo-layout.md").exists())

    def test_memory_utilities_cover_init_check_and_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            repo.mkdir()
            valid_memory = textwrap.dedent(
                """
                # MEMORY.md

                ## Current Objective
                - Keep the verification fixture green.

                ## Active Working Set
                - verification/

                ## Files Already Inspected
                - verification/README.md

                ## Important Findings
                - The fixture uses a strict timestamp.

                ## Decisions Already Made
                - Keep the file concise.

                ## Next Steps
                - Run the script tests.

                ## Stop Condition
                - Verification scripts pass.

                ## Last Updated
                - 2099-01-01 00:00 local time
                """
            ).strip()

            code, _, stderr = run_script(str(SCRIPTS_DIR / "init_memory.py"), str(repo))
            self.assertEqual(code, 0, stderr)
            self.assertTrue((repo / "MEMORY.md").exists())

            (repo / "MEMORY.md").write_text(valid_memory + "\n", encoding="utf-8")
            code, stdout, stderr = run_script(
                str(SCRIPTS_DIR / "check_memory_freshness.py"),
                str(repo),
                "--strict",
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("passed", stdout)

            code, stdout, stderr = run_script(
                str(SCRIPTS_DIR / "create_handoff_snapshot.py"),
                str(repo),
                "--title",
                "fixture handoff",
                "--from-memory",
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Created ", stdout)
            self.assertIn("fixture-handoff", stdout)

    def test_preview_context_bundle_emits_verification_metadata(self) -> None:
        code, stdout, stderr = run_script(
            str(SCRIPTS_DIR / "preview_context_bundle.py"),
            "backend-api-fastapi-polars",
            "--json",
        )
        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertTrue(payload["ranked_examples"])
        first = payload["ranked_examples"][0]
        self.assertIn("verification_level", first)
        self.assertIn("confidence", first)

    def test_prompt_first_repo_analyzer_works_on_valid_fixture(self) -> None:
        fixture = REPO_ROOT / "verification/fixtures/valid_repo"
        code, stdout, stderr = run_script(
            str(SCRIPTS_DIR / "prompt_first_repo_analyzer.py"),
            str(fixture),
            "--json",
        )
        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertEqual(payload["signals"]["archetypes"][0]["name"], "prompt-first-repo")

    def test_missing_manifest_fixture_is_intentionally_broken(self) -> None:
        fixture = REPO_ROOT / "verification/fixtures/invalid_repo_missing_manifest"
        self.assertFalse((fixture / "manifests").exists())


if __name__ == "__main__":
    unittest.main()
