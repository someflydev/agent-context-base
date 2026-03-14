from __future__ import annotations

import json
import unittest

from verification.helpers import REPO_ROOT, load_yaml_like


EXPECTED_TASK_ALIASES = {
    "research data sources": "context/workflows/research-data-sources.md",
    "add api source": "context/workflows/add-api-ingestion-source.md",
    "save raw downloads": "context/workflows/add-raw-download-archive.md",
    "classify records": "context/workflows/add-classification-step.md",
    "twice daily sync": "context/workflows/add-recurring-sync.md",
    "event driven sync": "context/workflows/add-event-driven-sync.md",
}


class DataAcquisitionContextTests(unittest.TestCase):
    def test_required_context_files_exist(self) -> None:
        required = (
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


if __name__ == "__main__":
    unittest.main()
