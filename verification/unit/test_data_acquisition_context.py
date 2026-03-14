from __future__ import annotations

import json
import unittest

from verification.helpers import REPO_ROOT, load_yaml_like


EXPECTED_TASK_ALIASES = {
    "research data sources": "context/workflows/research-data-sources.md",
    "generic acquisition guidance": "context/doctrine/data-acquisition-invariants.md",
    "add api source": "context/workflows/add-api-ingestion-source.md",
    "save raw downloads": "context/workflows/add-raw-download-archive.md",
    "classify records": "context/workflows/add-classification-step.md",
    "twice daily sync": "context/workflows/add-recurring-sync.md",
    "event driven sync": "context/workflows/add-event-driven-sync.md",
}


class DataAcquisitionContextTests(unittest.TestCase):
    def test_required_context_files_exist(self) -> None:
        required = (
            "context/doctrine/data-acquisition-invariants.md",
            "context/doctrine/data-acquisition-philosophy.md",
            "context/doctrine/raw-data-retention.md",
            "context/doctrine/sync-safety-rate-limits.md",
            "context/doctrine/source-research-discipline.md",
            "context/workflows/research-data-sources.md",
            "context/workflows/add-api-ingestion-source.md",
            "context/workflows/add-scraping-source.md",
            "context/workflows/add-raw-download-archive.md",
            "context/workflows/add-parser-normalizer.md",
            "context/workflows/add-classification-step.md",
            "context/workflows/add-recurring-sync.md",
            "context/workflows/add-event-driven-sync.md",
            "context/workflows/add-source-backoff-retry.md",
            "context/archetypes/data-acquisition-service.md",
            "context/archetypes/multi-source-sync-platform.md",
            "context/stacks/scraping-and-ingestion-patterns.md",
            "context/stacks/source-research-and-evaluation.md",
            "context/stacks/event-streaming-patterns.md",
            "docs/public-example-data-systems-readiness.md",
            "examples/canonical-data-acquisition/README.md",
            "examples/canonical-data-acquisition/language-support-matrix.yaml",
            "manifests/data-acquisition-service.yaml",
            "manifests/multi-source-sync-platform.yaml",
        )
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((REPO_ROOT / relative).exists(), relative)

    def test_alias_catalog_exposes_data_acquisition_intents(self) -> None:
        catalog = load_yaml_like(REPO_ROOT / "context/router/alias-catalog.yaml")
        tasks = {
            str(entry.get("alias", "")).strip(): str(entry.get("target", "")).strip()
            for entry in catalog.get("tasks", [])
            if isinstance(entry, dict)
        }
        for alias, target in EXPECTED_TASK_ALIASES.items():
            with self.subTest(alias=alias):
                self.assertEqual(tasks.get(alias), target)

    def test_manifests_reference_invariant_doc_and_index(self) -> None:
        for relative in (
            "manifests/data-acquisition-service.yaml",
            "manifests/multi-source-sync-platform.yaml",
        ):
            data = load_yaml_like(REPO_ROOT / relative)
            required_context = data.get("required_context", [])
            preferred_examples = data.get("preferred_examples", [])
            with self.subTest(manifest=relative):
                self.assertIn("context/doctrine/data-acquisition-invariants.md", required_context)
                self.assertIn("examples/canonical-data-acquisition/README.md", preferred_examples)
                self.assertIn("examples/canonical-data-acquisition/language-support-matrix.yaml", preferred_examples)

    def test_repo_signal_hints_cover_new_archetypes_stacks_and_workflows(self) -> None:
        data = json.loads((REPO_ROOT / "context/router/repo-signal-hints.json").read_text(encoding="utf-8"))
        stack_names = {entry["name"] for entry in data["stacks"]}
        archetype_names = {entry["name"] for entry in data["archetypes"]}
        workflow_names = {entry["name"] for entry in data["workflows"]}

        self.assertIn("scraping-and-ingestion-patterns", stack_names)
        self.assertIn("source-research-and-evaluation", stack_names)
        self.assertIn("event-streaming-patterns", stack_names)
        self.assertIn("data-acquisition-service", archetype_names)
        self.assertIn("multi-source-sync-platform", archetype_names)
        self.assertIn("research-data-sources", workflow_names)
        self.assertIn("add-api-ingestion-source", workflow_names)
        self.assertIn("add-recurring-sync", workflow_names)

    def test_support_matrix_declares_acquisition_capability_layer(self) -> None:
        data = load_yaml_like(REPO_ROOT / "verification/stack_support_matrix.yaml")
        capabilities = data.get("capabilities", [])
        entry = next(
            item
            for item in capabilities
            if isinstance(item, dict) and item.get("capability") == "canonical-data-acquisition"
        )
        stacks = {item["stack"] for item in entry["stacks"]}
        self.assertEqual(
            stacks,
            {
                "python-fastapi-uv-ruff-orjson-polars",
                "go-echo",
                "elixir-phoenix",
                "rust-axum-modern",
                "typescript-hono-bun",
                "nim-jester-happyx",
                "zig-zap-jetzig",
                "crystal-kemal-avram",
            },
        )

        expected_status = {
            "python-fastapi-uv-ruff-orjson-polars": ("behavior-verified", ["fastapi-source-sync-example"]),
            "go-echo": ("syntax-checked", ["go-echo-source-sync-example"]),
            "elixir-phoenix": ("structure-verified", ["phoenix-source-sync-example"]),
            "rust-axum-modern": ("syntax-checked", ["rust-axum-source-sync-example"]),
            "typescript-hono-bun": ("syntax-checked", ["typescript-hono-source-sync-example"]),
            "nim-jester-happyx": ("structure-verified", ["nim-jester-source-sync-example"]),
            "zig-zap-jetzig": ("structure-verified", ["zig-zap-source-sync-example"]),
            "crystal-kemal-avram": ("structure-verified", ["crystal-kemal-source-sync-example"]),
        }
        for item in entry["stacks"]:
            with self.subTest(stack=item["stack"]):
                self.assertEqual(item["status"], expected_status[item["stack"]][0])
                self.assertEqual(item["stack_specific_examples"], expected_status[item["stack"]][1])

    def test_public_readiness_note_mentions_layer_separation(self) -> None:
        text = (REPO_ROOT / "docs/public-example-data-systems-readiness.md").read_text(encoding="utf-8")
        self.assertIn("generic data acquisition invariants", text)
        self.assertIn("stack-specific real examples", text)
        self.assertIn("verification posture by language", text)


if __name__ == "__main__":
    unittest.main()
