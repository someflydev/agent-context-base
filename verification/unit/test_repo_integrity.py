from __future__ import annotations

import re
import sys
import unittest

from verification.helpers import (
    REPO_ROOT,
    VALID_VERIFICATION_LEVELS,
    load_registry,
    load_stack_matrix,
    registry_by_name,
    registry_by_path,
)

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from manifest_tools import normalize_string_list, parse_manifest  # noqa: E402


class RepoIntegrityTests(unittest.TestCase):
    def test_required_directories_exist(self) -> None:
        required = (
            "verification",
            "verification/policies",
            "verification/unit",
            "verification/scripts",
            "verification/examples/python",
            "verification/examples/nim",
            "verification/examples/crystal",
            "verification/examples/scala",
            "verification/examples/kotlin",
            "verification/examples/clojure",
            "verification/examples/zig",
            "verification/examples/go",
            "verification/examples/rust",
            "verification/examples/elixir",
            "verification/examples/data",
            "verification/scenarios/fastapi_min_app",
            "verification/scenarios/nim_jester_happyx_min_app",
            "verification/scenarios/crystal_kemal_avram_min_app",
            "verification/scenarios/scala_tapir_http4s_zio_min_app",
            "verification/scenarios/kotlin_http4k_exposed_min_app",
            "verification/scenarios/clojure_kit_nextjdbc_hiccup_min_app",
            "verification/scenarios/zig_zap_jetzig_min_app",
            "verification/scenarios/go_echo_min_app",
            "verification/scenarios/rust_axum_min_app",
            "verification/scenarios/polars_data_pipeline",
            "verification/fixtures/valid_repo",
            "verification/fixtures/invalid_repo_missing_manifest",
            "verification/fixtures/broken_prompt_sequence",
            "verification/fixtures/invalid_stack_reference",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((REPO_ROOT / relative).exists(), relative)

    def test_manifests_reference_existing_files(self) -> None:
        path_keys = (
            "required_context",
            "optional_context",
            "preferred_examples",
            "recommended_templates",
        )
        registry_paths = registry_by_path()
        for manifest_path in sorted((REPO_ROOT / "manifests").glob("*.yaml")):
            data = parse_manifest(manifest_path)
            for key in path_keys:
                for ref in normalize_string_list(data.get(key)):
                    with self.subTest(manifest=manifest_path.name, key=key, ref=ref):
                        self.assertTrue((REPO_ROOT / ref).exists(), ref)
                        if key == "preferred_examples":
                            self.assertIn(ref, registry_paths)

    def test_example_registry_paths_and_levels_are_valid(self) -> None:
        entries = load_registry()
        self.assertGreater(len(entries), 20)
        for entry in entries:
            path = str(entry.get("path", ""))
            level = str(entry.get("verification_level", ""))
            confidence = str(entry.get("confidence", ""))
            with self.subTest(path=path):
                self.assertTrue((REPO_ROOT / path).exists(), path)
                self.assertIn(level, VALID_VERIFICATION_LEVELS)
                self.assertIn(confidence, {"low", "medium", "high"})
                if entry.get("scenario_harness"):
                    harness = REPO_ROOT / "verification/scenarios" / str(entry["scenario_harness"])
                    self.assertTrue(harness.exists(), harness.as_posix())

    def test_stack_support_matrix_references_known_examples(self) -> None:
        known = registry_by_name()
        for entry in load_stack_matrix():
            stack = str(entry.get("stack", ""))
            verified = entry.get("verified_examples", [])
            self.assertTrue(stack)
            self.assertIsInstance(verified, list)
            for name in verified:
                with self.subTest(stack=stack, example=name):
                    self.assertIn(name, known)

    def test_docs_template_references_resolve(self) -> None:
        doc_paths = [
            REPO_ROOT / "README.md",
            *sorted((REPO_ROOT / "docs").glob("*.md")),
            *sorted((REPO_ROOT / "examples").glob("**/*.md")),
            REPO_ROOT / "scripts/README.md",
        ]
        pattern = re.compile(r"(templates/[A-Za-z0-9._/\-]+)")
        for doc_path in doc_paths:
            text = doc_path.read_text(encoding="utf-8")
            for match in pattern.finditer(text):
                template_ref = match.group(1).rstrip(").,")
                with self.subTest(doc=doc_path.name, template_ref=template_ref):
                    self.assertTrue((REPO_ROOT / template_ref).exists(), template_ref)


if __name__ == "__main__":
    unittest.main()
