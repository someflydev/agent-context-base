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
    def _run_checked_command(self, args: list[str], cwd: Path) -> str:
        result = run_command(args, cwd=cwd, timeout=240)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def _init_git_repo(self, repo: Path) -> None:
        self._run_checked_command(["git", "init"], cwd=repo)
        self._run_checked_command(["git", "config", "user.name", "ACB Test"], cwd=repo)
        self._run_checked_command(["git", "config", "user.email", "acb-test@example.com"], cwd=repo)

    def _public_root_entries(self, target: Path) -> set[str]:
        return {path.name for path in target.iterdir() if not path.name.startswith(".")}

    def _repo_local_prompt_paths(self, text: str) -> set[str]:
        candidates = set(re.findall(r"`([^`\n]+)`", text))
        prefixes = (
            ".prompts/",
            ".acb/",
            "manifests/",
            "context/",
            "examples/",
            "templates/",
            "docs/",
            "scripts/",
            "tests/",
        )
        exact = {"AGENT.md", "CLAUDE.md", ".generated-profile.yaml", ".acb/.generated-profile.yaml", "README.md"}
        return {
            candidate
            for candidate in candidates
            if (candidate.startswith(prefixes) or candidate in exact) and not candidate.endswith("/")
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
            self.assertEqual(self._public_root_entries(target), {"AGENT.md", "CLAUDE.md"})
            self.assertFalse((target / "scripts").exists())
            self.assertTrue((target / ".acb/manifests/project-profile.yaml").exists())
            self.assertTrue((target / ".acb/scripts/work.py").exists())
            self.assertTrue((target / ".acb/manifests/base/prompt-first-meta-repo.yaml").exists())
            self.assertTrue((target / ".acb/context/doctrine/core-principles.md").exists())
            self.assertTrue((target / ".acb/examples/canonical-prompts/001-bootstrap-repo.txt").exists())
            profile = (target / ".acb/manifests/project-profile.yaml").read_text(encoding="utf-8")
            prompt_01 = (target / ".prompts/PROMPT_01.txt").read_text(encoding="utf-8")
            prompt_04 = (target / ".prompts/PROMPT_04.txt").read_text(encoding="utf-8")
            agent_md = (target / "AGENT.md").read_text(encoding="utf-8")
            self.assertIn("prompts_md_generated: false", profile)
            self.assertIn("prompt_directory: .prompts", profile)
            self.assertIn("repo_local_profile_path: .acb/manifests/project-profile.yaml", profile)
            self.assertIn("- .acb/manifests/base/prompt-first-meta-repo.yaml", profile)
            self.assertIn("- .acb/context/doctrine/core-principles.md", profile)
            self.assertIn("- .prompts/PROMPT_04.txt", profile)
            self.assertIn("route: .prompts/PROMPT_01.txt", profile)
            self.assertIn("generated_profile_path: .acb/.generated-profile.yaml", profile)
            self.assertIn("source_example_lineage_note:", profile)
            self.assertNotIn("--use-example", profile)
            self.assertIn("descendant of `agent-context-base`", prompt_01)
            self.assertIn("Treat the vendored base manifests", prompt_01)
            self.assertIn("`.acb/manifests/project-profile.yaml`", prompt_01)
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
            profile = (target / ".acb/manifests/project-profile.yaml").read_text(encoding="utf-8")
            self.assertIn("derived_context_mode: maximal", profile)
            self.assertIn("vendored_base_root: .acb", profile)
            self.assertIn("generated_profile_path: .acb/.generated-profile.yaml", profile)
            self.assertIn("maximal_bundle_policy:", profile)
            self.assertIn("name: derived-maximal-prompt-first-continuation-v1", profile)
            self.assertIn("mode_vendored_paths:", profile)
            self.assertIn("maximal_bundle_records:", profile)
            self.assertIn("- .acb/context/anchors/prompt-first.md", profile)
            self.assertIn("- .acb/examples/canonical-workflows/README.md", profile)

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
            compact_profile = (compact_target / ".acb/manifests/project-profile.yaml").read_text(encoding="utf-8")
            maximal_profile = (maximal_target / ".acb/manifests/project-profile.yaml").read_text(encoding="utf-8")
            self.assertGreater(len(maximal_files), len(compact_files))
            self.assertEqual(self._public_root_entries(compact_target), {"AGENT.md", "CLAUDE.md"})
            self.assertEqual(self._public_root_entries(maximal_target), {"AGENT.md", "CLAUDE.md"})
            self.assertNotIn("context/anchors/prompt-first.md", compact_profile)
            self.assertIn(".acb/context/anchors/prompt-first.md", maximal_profile)
            self.assertFalse((compact_target / "examples/canonical-workflows/README.md").exists())
            self.assertTrue((compact_target / ".acb/manifests/base/prompt-first-meta-repo.yaml").exists())
            self.assertFalse((maximal_target / "examples/canonical-workflows/README.md").exists())
            self.assertTrue((maximal_target / ".acb/examples/canonical-workflows/README.md").exists())
            self.assertTrue((maximal_target / ".acb/context/archetypes/multi-backend-service.md").exists())
            self.assertTrue((maximal_target / ".acb/context/stacks/go-echo.md").exists())
            for leaked_root in ("context", "examples", "templates", "docs", "scripts", "manifests"):
                self.assertFalse((maximal_target / leaked_root).exists(), leaked_root)
                self.assertFalse((compact_target / leaked_root).exists(), leaked_root)

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
                profile_path = parent / child / ".acb/manifests/project-profile.yaml"
                self.assertTrue(profile_path.exists(), child)
                self.assertTrue((parent / child / ".acb/context/anchors/prompt-first.md").exists(), child)
                self.assertIn("derived_context_mode: maximal", profile_path.read_text(encoding="utf-8"))

    def test_new_repo_maximal_guidance_only_points_at_present_repo_local_bundle_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = self._generate_derived_repo(
                Path(temp_dir),
                "operator-surface",
                derived_context_mode="maximal",
            )
            profile = (target / ".acb/manifests/project-profile.yaml").read_text(encoding="utf-8")
            prompt_01 = (target / ".prompts/PROMPT_01.txt").read_text(encoding="utf-8")
            agent_md = (target / "AGENT.md").read_text(encoding="utf-8")
            claude_md = (target / "CLAUDE.md").read_text(encoding="utf-8")
            for relative_path in (
                ".acb/context/anchors/prompt-first.md",
                ".acb/context/workflows/generate-prompt-sequence.md",
                ".acb/context/skills/context-bundle-assembly.md",
                ".acb/examples/canonical-prompts/README.md",
                ".acb/examples/canonical-prompts/prompt-first-layout-example.md",
                ".acb/examples/canonical-workflows/README.md",
                ".acb/templates/manifest/manifest.template.yaml",
            ):
                self.assertTrue((target / relative_path).exists(), relative_path)
                self.assertIn(relative_path, profile)
            self.assertIn("Derived context mode: `maximal`.", prompt_01)
            self.assertIn("`.acb/context/anchors/prompt-first.md`", prompt_01)
            self.assertIn("`.acb/context/workflows/generate-prompt-sequence.md`", prompt_01)
            self.assertIn("`.acb/examples/canonical-prompts/prompt-first-layout-example.md`", prompt_01)
            self.assertIn("`.acb/.generated-profile.yaml`", agent_md)
            self.assertIn("`.acb/manifests/project-profile.yaml`", agent_md)
            self.assertIn("`.acb/manifests/base/*.yaml`", agent_md)
            self.assertIn("`.acb/docs/repo-purpose.md`", agent_md)
            self.assertIn("`.acb/docs/repo-layout.md`", agent_md)
            self.assertIn("`.acb/.generated-profile.yaml`", claude_md)
            self.assertIn("`.acb/manifests/project-profile.yaml`", claude_md)
            self.assertIn("`.acb/manifests/base/*.yaml`", claude_md)
            self.assertIn("`.acb/docs/repo-purpose.md`", claude_md)
            self.assertIn("`.acb/docs/repo-layout.md`", claude_md)

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
            profile = (target / ".acb/manifests/project-profile.yaml").read_text(encoding="utf-8")
            self.assertIn("derived_context_mode: compact", profile)
            self.assertIn("vendored_base_root: .acb", profile)
            self.assertIn("generated_profile_path: .acb/.generated-profile.yaml", profile)
            self.assertIn("mode_vendored_paths:", profile)
            self.assertNotIn("context/anchors/prompt-first.md", profile)
            self.assertFalse((target / "context/anchors/prompt-first.md").exists())
            self.assertTrue((target / ".acb").exists())
            self.assertEqual(self._public_root_entries(target), {"AGENT.md", "CLAUDE.md"})

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
            profile = (target / ".acb/manifests/project-profile.yaml").read_text(encoding="utf-8")
            self.assertTrue((target / ".acb/manifests/base/backend-api-fastapi-polars.yaml").exists())
            self.assertTrue((target / ".acb/manifests/base/data-acquisition-service.yaml").exists())
            self.assertIn("vendored_base_manifests_dir: .acb/manifests/base", profile)
            self.assertIn("- .acb/manifests/base/backend-api-fastapi-polars.yaml", profile)
            self.assertIn("- .acb/manifests/base/data-acquisition-service.yaml", profile)

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

    def test_new_repo_acb_smoke_script_covers_expected_cases(self) -> None:
        script_path = REPO_ROOT / "scripts" / "smoke" / "new_repo_acb_smoke.sh"
        script_text = script_path.read_text(encoding="utf-8")
        self.assertTrue(script_path.exists())
        self.assertIn('TIMESTAMP="$(date "+%Y%m%d-%H%M%S")"', script_text)
        self.assertIn("/tmp/smoke-acb-${TIMESTAMP}-${COMMIT_ID}", script_text)
        self.assertIn("git -C \"$REPO_ROOT\" rev-parse --short HEAD", script_text)
        self.assertIn("prompt-kit ordinary", script_text)
        self.assertIn("--use-example 1", script_text)
        self.assertIn("--derived-example operator-surface", script_text)
        self.assertIn("--derived-example team-a", script_text)
        self.assertIn("--derived-context-mode maximal", script_text)

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
                "--initial-prompt-text",
                "Build a prompt-first repo for evaluating prompt variants against a small rubric.",
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Generated starter repo", stdout)
            self.assertTrue((target / ".prompts/001-bootstrap-repo.txt").exists())
            self.assertTrue((target / ".prompts/initial-prompt.txt").exists())
            self.assertTrue((target / "AGENT.md").exists())
            self.assertFalse((target / "PROMPTS.md").exists())
            self.assertTrue((target / ".acb/manifests/project-profile.yaml").exists())
            self.assertTrue((target / ".acb/.generated-profile.yaml").exists())
            self.assertTrue((target / ".acb/manifests/base/prompt-first-meta-repo.yaml").exists())
            self.assertTrue((target / ".acb/context/doctrine/core-principles.md").exists())
            self.assertTrue((target / ".acb/examples/canonical-prompts/001-bootstrap-repo.txt").exists())
            self.assertTrue((target / ".acb/examples/canonical-prompts/README.md").exists())
            self.assertTrue((target / ".acb/templates/memory/MEMORY.template.md").exists())
            self.assertTrue((target / ".acb/templates/memory/HANDOFF-SNAPSHOT.template.md").exists())
            self.assertTrue((target / ".acb/templates/prompt-first/001-bootstrap.template.txt").exists())
            self.assertTrue((target / "scripts/work.py").exists())
            self.assertTrue((target / ".acb/scripts/work.py").exists())
            self.assertTrue((target / ".acb/scripts/init_memory.py").exists())
            self.assertTrue((target / ".acb/scripts/check_memory_freshness.py").exists())
            self.assertTrue((target / ".acb/scripts/create_handoff_snapshot.py").exists())
            self.assertTrue((target / ".acb/scripts/acb_inspect.py").exists())
            self.assertTrue((target / ".acb/scripts/acb_verify.py").exists())
            self.assertTrue((target / ".acb/validation/COVERAGE.md").exists())
            self.assertTrue((target / ".acb/validation/COVERAGE.json").exists())
            self.assertTrue((target / ".acb/docs/session-start.md").exists())
            self.assertTrue((target / ".acb/generation-report.json").exists())
            self.assertFalse((target / "README.md").exists())
            self.assertFalse((target / "docs").exists())
            profile = (target / ".acb/manifests/project-profile.yaml").read_text(encoding="utf-8")
            audit = json.loads((target / ".acb/generation-report.json").read_text(encoding="utf-8"))
            self.assertIn("repo_local_profile_path: .acb/manifests/project-profile.yaml", profile)
            self.assertIn("generated_profile_path: .acb/.generated-profile.yaml", profile)
            self.assertIn("vendored_base_root: .acb", profile)
            self.assertIn("ordinary_context_mode: compact-vendored-support-bundle", profile)
            self.assertIn("manifest_bundle_startup_paths:", profile)
            self.assertIn("repo_local_routing_model_paths:", profile)
            self.assertIn("local_canonical_examples_available:", profile)
            self.assertIn("local_templates_available:", profile)
            self.assertIn("local_continuity_tools_available:", profile)
            self.assertIn("- .acb/examples/canonical-prompts/001-bootstrap-repo.txt", profile)
            self.assertIn("- .acb/templates/memory/MEMORY.template.md", profile)
            self.assertIn("- .acb/scripts/init_memory.py", profile)
            self.assertIn("- .acb/docs/session-start.md", profile)
            self.assertIn(".acb/templates/memory/MEMORY.template.md", audit["vendored_support_paths"])
            self.assertIn(".acb/scripts/create_handoff_snapshot.py", audit["vendored_support_paths"])
            self.assertIn(".acb/scripts/acb_verify.py", audit["vendored_support_paths"])
            self.assertEqual(audit["startup_bundle_metadata"]["ordinary_context_mode"], "compact-vendored-support-bundle")

            code, stdout, stderr = run_script("scripts/validate_repo.py", cwd=target)
            self.assertEqual(code, 0, stderr)
            self.assertIn("repo validation passed", stdout)

    def test_new_repo_use_example_vendors_compact_ordinary_support_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "001-partner-data-enrichment"
            code, stdout, stderr = run_script(
                str(SCRIPTS_DIR / "new_repo.py"),
                "--use-example",
                "1",
                "--target-dir",
                str(target),
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Generated starter repo", stdout)
            self.assertTrue((target / ".acb/manifests/base/backend-api-fastapi-polars.yaml").exists())
            self.assertTrue((target / ".acb/context/doctrine/core-principles.md").exists())
            self.assertTrue((target / ".acb/context/workflows/add-api-endpoint.md").exists())
            self.assertTrue((target / ".acb/examples/canonical-api/fastapi-endpoint-example.py").exists())
            self.assertTrue((target / ".acb/examples/canonical-api/README.md").exists())
            self.assertTrue((target / ".acb/templates/memory/MEMORY.template.md").exists())
            self.assertTrue((target / ".acb/templates/compose/docker-compose.template.yaml").exists())
            self.assertTrue((target / ".acb/scripts/init_memory.py").exists())
            self.assertTrue((target / ".acb/scripts/acb_verify.py").exists())
            self.assertTrue((target / ".acb/docs/session-start.md").exists())

            profile = (target / ".acb/manifests/project-profile.yaml").read_text(encoding="utf-8")
            audit = json.loads((target / ".acb/generation-report.json").read_text(encoding="utf-8"))
            for relative_path in (
                ".acb/context/doctrine/core-principles.md",
                ".acb/context/stacks/python-fastapi-uv-ruff-orjson-polars.md",
                ".acb/examples/canonical-api/fastapi-endpoint-example.py",
                ".acb/templates/compose/docker-compose.template.yaml",
                ".acb/scripts/init_memory.py",
            ):
                self.assertIn(relative_path, profile)
                self.assertTrue((target / relative_path).exists(), relative_path)
            self.assertIn("ordinary_context_mode: compact-vendored-support-bundle", profile)
            self.assertIn(".acb/examples/canonical-api/fastapi-endpoint-example.py", audit["vendored_support_paths"])
            self.assertIn(".acb/scripts/init_memory.py", audit["vendored_support_paths"])
            self.assertIn(".acb/scripts/acb_verify.py", audit["vendored_support_paths"])
            routing_model = audit["startup_bundle_metadata"]["repo_local_routing_model_paths"]
            self.assertIn(".acb/manifests/project-profile.yaml", routing_model)
            self.assertIn(".prompts/001-bootstrap-repo.txt", routing_model)

            code, stdout, stderr = run_script(".acb/scripts/acb_inspect.py", cwd=target)
            self.assertEqual(code, 0, stderr)
            self.assertIn("ACB payload summary", stdout)
            self.assertIn("Canonical source modules", stdout)

            code, stdout, stderr = run_script(".acb/scripts/acb_verify.py", cwd=target)
            self.assertEqual(code, 0, stderr)
            self.assertIn("local payload drift: none", stdout)

    def test_new_repo_snapshots_initial_prompt_and_audit_for_standard_repo(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "ml-gateway"
            code, stdout, stderr = run_script(
                str(SCRIPTS_DIR / "new_repo.py"),
                "ml-gateway",
                "--target-dir",
                str(target),
                "--archetype",
                "multi-backend-service",
                "--primary-stack",
                "go-echo",
                "--storage-service",
                "postgres",
                "--storage-service",
                "nats",
                "--initial-prompt-text",
                "Build a Go gateway and Python ML scorer with NATS for emitted events and PostgreSQL for durable request state.",
            )
            self.assertEqual(code, 0, stderr)
            self.assertIn("Generated starter repo", stdout)
            self.assertTrue((target / ".prompts/001-bootstrap-repo.txt").exists())
            self.assertTrue((target / ".prompts/002-refine-test-surface.txt").exists())
            self.assertTrue((target / ".prompts/initial-prompt.txt").exists())
            self.assertTrue((target / ".acb/generation-report.json").exists())

            audit = json.loads((target / ".acb/generation-report.json").read_text(encoding="utf-8"))
            self.assertEqual(audit["support_services"]["selected"], ["postgres", "nats"])
            self.assertEqual(audit["initial_prompt"]["path"], ".prompts/initial-prompt.txt")
            self.assertIn(".prompts/initial-prompt.txt", audit["prompt_files"])

            profile = (target / ".acb/manifests/project-profile.yaml").read_text(encoding="utf-8")
            env_text = (target / ".env").read_text(encoding="utf-8")
            self.assertIn("generation_audit_path: .acb/generation-report.json", profile)
            self.assertIn("repo_local_profile_path: .acb/manifests/project-profile.yaml", profile)
            self.assertIn("generated_profile_path: .acb/.generated-profile.yaml", profile)
            self.assertIn("prompt_directory: .prompts", profile)
            self.assertIn("DATABASE_URL=postgresql://app:app@127.0.0.1:", env_text)
            self.assertIn("NATS_URL=nats://127.0.0.1:", env_text)

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
            self.assertTrue((target / "AGENT.md").exists())
            self.assertTrue((target / "CLAUDE.md").exists())
            self.assertTrue((target / "scripts/work.py").exists())
            self.assertTrue((target / ".prompts/001-bootstrap-repo.txt").exists())
            self.assertTrue((target / ".acb/manifests/project-profile.yaml").exists())
            self.assertTrue((target / ".acb/.generated-profile.yaml").exists())
            self.assertTrue((target / ".acb/generation-report.json").exists())
            gitignore = (target / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("PLAN.md", gitignore)
            self.assertIn("context/TASK.md", gitignore)
            self.assertIn("context/SESSION.md", gitignore)
            self.assertIn("context/MEMORY.md", gitignore)

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
            self.assertTrue((repo / "context/MEMORY.md").exists())

            (repo / "context/MEMORY.md").write_text(valid_memory + "\n", encoding="utf-8")
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

    def test_work_script_scaffolds_and_resumes_runtime_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            scripts_dir = repo / "scripts"
            scripts_dir.mkdir(parents=True)
            (repo / "AGENT.md").write_text("# AGENT.md\n", encoding="utf-8")
            (repo / ".git").mkdir()
            (scripts_dir / "work.py").write_text((SCRIPTS_DIR / "work.py").read_text(encoding="utf-8"), encoding="utf-8")

            code, stdout, stderr = run_script(str(repo / "scripts/work.py"), "checkpoint", cwd=repo)
            self.assertEqual(code, 0, stderr)
            self.assertIn("Created PLAN.md", stdout)
            self.assertTrue((repo / "PLAN.md").exists())
            self.assertTrue((repo / "context/TASK.md").exists())
            self.assertTrue((repo / "context/SESSION.md").exists())
            self.assertTrue((repo / "context/MEMORY.md").exists())

            code, stdout, stderr = run_script(str(repo / "scripts/work.py"), "resume", cwd=repo)
            self.assertEqual(code, 0, stderr)
            self.assertIn("Runtime Resume", stdout)
            self.assertIn("context/TASK.md", stdout)
            self.assertIn("context/SESSION.md", stdout)
            self.assertIn("Git signals:", stdout)
            self.assertIn("Working signals:", stdout)

    def test_work_script_prefers_repo_local_example_templates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            scripts_dir = repo / "scripts"
            context_dir = repo / "context"
            scripts_dir.mkdir(parents=True)
            context_dir.mkdir(parents=True)
            (repo / "AGENT.md").write_text("# AGENT.md\n", encoding="utf-8")
            (repo / ".git").mkdir()
            (scripts_dir / "work.py").write_text((SCRIPTS_DIR / "work.py").read_text(encoding="utf-8"), encoding="utf-8")
            (repo / "PLAN.example.md").write_text("# custom plan\n", encoding="utf-8")
            (context_dir / "TASK.example.md").write_text("# custom task\n", encoding="utf-8")

            code, stdout, stderr = run_script(str(repo / "scripts/work.py"), "checkpoint", cwd=repo)
            self.assertEqual(code, 0, stderr)
            self.assertIn("Created PLAN.md from PLAN.example.md", stdout)
            self.assertIn("Created context/TASK.md from context/TASK.example.md", stdout)
            self.assertEqual((repo / "PLAN.md").read_text(encoding="utf-8"), "# custom plan\n")
            self.assertEqual((context_dir / "TASK.md").read_text(encoding="utf-8"), "# custom task\n")
            self.assertTrue((context_dir / "SESSION.md").exists())
            self.assertTrue((context_dir / "MEMORY.md").exists())

    def test_work_script_reports_git_anchor_and_resume_signals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Path(temp_dir) / "repo"
            scripts_dir = repo / "scripts"
            context_dir = repo / "context"
            prompts_dir = repo / ".prompts"
            templates_dir = repo / "templates" / "readme"
            scripts_dir.mkdir(parents=True)
            context_dir.mkdir(parents=True)
            prompts_dir.mkdir(parents=True)
            templates_dir.mkdir(parents=True)
            (repo / "AGENT.md").write_text("# AGENT.md\n", encoding="utf-8")
            (scripts_dir / "work.py").write_text((SCRIPTS_DIR / "work.py").read_text(encoding="utf-8"), encoding="utf-8")
            (repo / "PLAN.md").write_text(
                textwrap.dedent(
                    """\
                    # PLAN.md

                    ## Active Phase
                    - Runtime hardening

                    ## Milestones
                    - Improve fresh-session signals.

                    ## Near-Term Focus
                    - Keep the tool small.
                    """
                ),
                encoding="utf-8",
            )
            (context_dir / "TASK.md").write_text(
                textwrap.dedent(
                    """\
                    # TASK.md

                    ## Current Slice
                    - Improve resume output.

                    ## Success Criteria
                    - Fresh sessions restart cleanly.

                    ## Immediate Steps
                    - Review the runtime workflow docs after validating the command output.
                    """
                ),
                encoding="utf-8",
            )
            (context_dir / "SESSION.md").write_text(
                textwrap.dedent(
                    """\
                    # SESSION.md

                    ## Current Status
                    - The runtime workflow is mid-hardening.

                    ## Next Safe Step
                    - Run the focused verification path.
                    """
                ),
                encoding="utf-8",
            )
            (context_dir / "MEMORY.md").write_text(
                textwrap.dedent(
                    """\
                    # MEMORY.md

                    ## Durable Rules
                    - Keep runtime notes local.
                    """
                ),
                encoding="utf-8",
            )
            (prompts_dir / "PROMPT_01.txt").write_text("bootstrap\n", encoding="utf-8")

            self._init_git_repo(repo)
            self._run_checked_command(["git", "add", "."], cwd=repo)
            self._run_checked_command(["git", "commit", "-m", "initial runtime state"], cwd=repo)

            (prompts_dir / "PROMPT_02.txt").write_text("follow-up\n", encoding="utf-8")
            (templates_dir / "README.template.md").write_text("# template\n", encoding="utf-8")
            self._run_checked_command(["git", "add", "."], cwd=repo)
            self._run_checked_command(["git", "commit", "-m", "touch prompt and template surfaces"], cwd=repo)

            code, stdout, stderr = run_script(str(repo / "scripts/work.py"), "resume", cwd=repo)
            self.assertEqual(code, 0, stderr)
            self.assertIn("Last commit:", stdout)
            self.assertIn("Next concrete step: Run the focused verification path.", stdout)
            self.assertIn("TASK fallback step: Review the runtime workflow docs after validating the command output.", stdout)
            self.assertIn("PLAN review:", stdout)
            self.assertIn("prompt-sequence files changed", stdout)
            self.assertIn("Memory promotion hint:", stdout)

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
