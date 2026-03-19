from __future__ import annotations

import json
import re
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
    def _repo_local_prompt_paths(self, text: str) -> set[str]:
        candidates = set(re.findall(r"`([^`\n]+)`", text))
        prefixes = (
            ".prompts/",
            "manifests/",
            "context/",
            "examples/",
            "templates/",
            "docs/",
            "scripts/",
            "tests/",
        )
        exact = {"AGENT.md", "CLAUDE.md", ".generated-profile.yaml", "README.md"}
        return {
            candidate
            for candidate in candidates
            if candidate.startswith(prefixes) or candidate in exact
        }

    def _generate_derived_repo(
        self,
        parent: Path,
        name: str,
        *,
        derived_context_mode: str | None = None,
    ) -> Path:
        args = [
            str(SCRIPTS_DIR / "new_repo.py"),
            "--derived-example",
            name,
            "--target-dir",
            str(parent),
        ]
        if derived_context_mode is not None:
            args.extend(["--derived-context-mode", derived_context_mode])
        code, _, stderr = run_script(*args)
        self.assertEqual(code, 0, stderr)
        return parent / name

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
        self.assertNotIn("--use-example", stdout)

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
            self.assertFalse((target / "PROMPTS.md").exists())
            self.assertTrue((target / ".prompts/PROMPT_01.txt").exists())
            self.assertTrue((target / ".prompts/PROMPT_04.txt").exists())
            self.assertTrue((target / "manifests/project-profile.yaml").exists())
            self.assertTrue((target / "manifests/base/prompt-first-meta-repo.yaml").exists())
            self.assertTrue((target / "context/doctrine/core-principles.md").exists())
            self.assertTrue((target / "examples/canonical-prompts/001-bootstrap-repo.txt").exists())
            profile = (target / "manifests/project-profile.yaml").read_text(encoding="utf-8")
            prompt_01 = (target / ".prompts/PROMPT_01.txt").read_text(encoding="utf-8")
            prompt_04 = (target / ".prompts/PROMPT_04.txt").read_text(encoding="utf-8")
            agent_md = (target / "AGENT.md").read_text(encoding="utf-8")
            self.assertIn("prompts_md_generated: false", profile)
            self.assertIn("prompt_directory: .prompts", profile)
            self.assertIn("- manifests/base/prompt-first-meta-repo.yaml", profile)
            self.assertIn("- context/doctrine/core-principles.md", profile)
            self.assertIn("- .prompts/PROMPT_04.txt", profile)
            self.assertIn("route: .prompts/PROMPT_01.txt", profile)
            self.assertIn("source_example_lineage_note:", profile)
            self.assertNotIn("--use-example", profile)
            self.assertIn("descendant of `agent-context-base`", prompt_01)
            self.assertIn("Treat the vendored base manifests", prompt_01)
            self.assertNotIn("--use-example", prompt_01)
            self.assertIn("Continue creating or refining prompt files in `.prompts/`", prompt_04)
            self.assertNotIn("--use-example", prompt_04)
            self.assertNotIn("tool-invocation-discipline.md", agent_md)

    def test_new_repo_maximal_leaf_records_mode_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = self._generate_derived_repo(
                Path(temp_dir),
                "operator-surface",
                derived_context_mode="maximal",
            )
            profile = (target / "manifests/project-profile.yaml").read_text(encoding="utf-8")
            self.assertIn("derived_context_mode: maximal", profile)
            self.assertIn("maximal_bundle_policy:", profile)
            self.assertIn("name: derived-maximal-prompt-first-continuation-v1", profile)
            self.assertIn("mode_vendored_paths:", profile)
            self.assertIn("maximal_bundle_records:", profile)
            self.assertIn("- context/anchors/prompt-first.md", profile)
            self.assertIn("- examples/canonical-workflows/README.md", profile)

    def test_new_repo_maximal_leaf_vendors_larger_bundle_than_compact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            (parent / "compact-parent").mkdir()
            (parent / "maximal-parent").mkdir()
            compact_target = self._generate_derived_repo(parent / "compact-parent", "ml-gateway-intelligence")
            maximal_target = self._generate_derived_repo(
                parent / "maximal-parent",
                "ml-gateway-intelligence",
                derived_context_mode="maximal",
            )
            compact_files = [path for path in compact_target.rglob("*") if path.is_file()]
            maximal_files = [path for path in maximal_target.rglob("*") if path.is_file()]
            compact_profile = (compact_target / "manifests/project-profile.yaml").read_text(encoding="utf-8")
            maximal_profile = (maximal_target / "manifests/project-profile.yaml").read_text(encoding="utf-8")
            self.assertGreater(len(maximal_files), len(compact_files))
            self.assertNotIn("context/anchors/prompt-first.md", compact_profile)
            self.assertIn("context/anchors/prompt-first.md", maximal_profile)
            self.assertFalse((compact_target / "examples/canonical-workflows/README.md").exists())
            self.assertTrue((maximal_target / "examples/canonical-workflows/README.md").exists())
            self.assertTrue((maximal_target / "context/archetypes/multi-backend-service.md").exists())
            self.assertTrue((maximal_target / "context/stacks/go-echo.md").exists())

    def test_new_repo_maximal_team_selector_generates_one_child_per_leaf(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            code, _, stderr = run_script(
                str(SCRIPTS_DIR / "new_repo.py"),
                "--derived-example",
                "team-a",
                "--derived-context-mode",
                "maximal",
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
                profile_path = parent / child / "manifests/project-profile.yaml"
                self.assertTrue(profile_path.exists(), child)
                self.assertTrue((parent / child / "context/anchors/prompt-first.md").exists(), child)
                self.assertIn("derived_context_mode: maximal", profile_path.read_text(encoding="utf-8"))

    def test_new_repo_maximal_guidance_only_points_at_present_repo_local_bundle_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = self._generate_derived_repo(
                Path(temp_dir),
                "operator-surface",
                derived_context_mode="maximal",
            )
            profile = (target / "manifests/project-profile.yaml").read_text(encoding="utf-8")
            prompt_01 = (target / ".prompts/PROMPT_01.txt").read_text(encoding="utf-8")
            agent_md = (target / "AGENT.md").read_text(encoding="utf-8")
            claude_md = (target / "CLAUDE.md").read_text(encoding="utf-8")
            for relative_path in (
                "context/anchors/prompt-first.md",
                "context/workflows/generate-prompt-sequence.md",
                "context/skills/context-bundle-assembly.md",
                "examples/canonical-prompts/README.md",
                "examples/canonical-prompts/prompt-first-layout-example.md",
                "examples/canonical-workflows/README.md",
                "templates/manifest/manifest.template.yaml",
            ):
                self.assertTrue((target / relative_path).exists(), relative_path)
                self.assertIn(relative_path, profile)
            self.assertIn("Derived context mode: `maximal`.", prompt_01)
            self.assertIn("`context/anchors/prompt-first.md`", prompt_01)
            self.assertIn("`context/workflows/generate-prompt-sequence.md`", prompt_01)
            self.assertIn("`examples/canonical-prompts/prompt-first-layout-example.md`", prompt_01)
            self.assertIn("derived_context_mode: maximal", agent_md)
            self.assertIn("derived_context_mode: maximal", claude_md)

    def test_new_repo_maximal_prompt_sequence_only_references_existing_repo_local_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = self._generate_derived_repo(
                Path(temp_dir),
                "operator-surface",
                derived_context_mode="maximal",
            )
            for prompt_name in ("PROMPT_01.txt", "PROMPT_02.txt", "PROMPT_03.txt", "PROMPT_04.txt"):
                prompt_text = (target / ".prompts" / prompt_name).read_text(encoding="utf-8")
                for relative_path in self._repo_local_prompt_paths(prompt_text):
                    self.assertTrue((target / relative_path).exists(), f"{prompt_name}: {relative_path}")

    def test_new_repo_default_derived_context_mode_remains_compact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = self._generate_derived_repo(Path(temp_dir), "operator-surface")
            profile = (target / "manifests/project-profile.yaml").read_text(encoding="utf-8")
            self.assertIn("derived_context_mode: compact", profile)
            self.assertIn("mode_vendored_paths:", profile)
            self.assertNotIn("context/anchors/prompt-first.md", profile)
            self.assertFalse((target / "context/anchors/prompt-first.md").exists())

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
            self.assertFalse((target / "PROMPTS.md").exists())
            self.assertTrue((target / "manifests/base/prompt-first-meta-repo.yaml").exists())
            self.assertTrue((target / "context/doctrine/core-principles.md").exists())
            self.assertTrue((target / "examples/canonical-prompts/001-bootstrap-repo.txt").exists())
            self.assertFalse((target / "README.md").exists())
            self.assertFalse((target / "docs").exists())

            code, stdout, stderr = run_script("scripts/validate_repo.py", cwd=target)
            self.assertEqual(code, 0, stderr)
            self.assertIn("repo validation passed", stdout)

    def test_prompt_first_repo_analyzer_accepts_generated_repo_without_prompts_md(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "prompt-kit"
            code, _, stderr = run_script(
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

            code, stdout, stderr = run_script(
                str(SCRIPTS_DIR / "prompt_first_repo_analyzer.py"),
                str(target),
                "--json",
            )
            self.assertEqual(code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["signals"]["archetypes"][0]["name"], "prompt-first-repo")
            self.assertEqual(payload["signals"]["stacks"][0]["name"], "prompt-first-repo")

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
