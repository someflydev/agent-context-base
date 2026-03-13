from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT, load_yaml_like


FORBIDDEN_PATTERNS = (
    re.compile(r"<[^>]+>"),
    re.compile(r"\bTODO\b", flags=re.IGNORECASE),
    re.compile(r"\bTBD\b", flags=re.IGNORECASE),
)


JSON_FILES = {
    "examples/canonical-dokku/app-json-example.json": {"name", "description", "scripts", "env"},
    "examples/canonical-observability/structured-log-example.json": {
        "timestamp",
        "level",
        "service",
        "event",
        "repo_profile",
    },
    "examples/canonical-observability/trace-span-example.json": {
        "trace_id",
        "span_id",
        "name",
        "attributes",
    },
    "examples/fixtures/minimal-report-runs.json": set(),
}

JSONL_FILES = {
    "examples/fixtures/minimal-document-corpus.jsonl": {"doc_id", "title", "body"},
}

YAML_FILES = {
    "examples/canonical-rag/local-rag-index-config-example.yaml": {
        "corpus_dir",
        "collection_name",
        "vector_store",
        "metadata_fields",
        "smoke_query",
    },
}


class DataExampleTests(unittest.TestCase):
    def test_json_examples_load_and_have_required_keys(self) -> None:
        for relative, required_keys in JSON_FILES.items():
            path = REPO_ROOT / relative
            with self.subTest(path=relative):
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    self.assertTrue(required_keys.issubset(data.keys()))
                else:
                    self.assertIsInstance(data, list)
                text = path.read_text(encoding="utf-8")
                for pattern in FORBIDDEN_PATTERNS:
                    self.assertIsNone(pattern.search(text))

    def test_yaml_examples_load_and_have_required_keys(self) -> None:
        for relative, required_keys in YAML_FILES.items():
            path = REPO_ROOT / relative
            with self.subTest(path=relative):
                data = load_yaml_like(path)
                self.assertTrue(required_keys.issubset(data.keys()))
                text = path.read_text(encoding="utf-8")
                for pattern in FORBIDDEN_PATTERNS:
                    self.assertIsNone(pattern.search(text))

    def test_jsonl_examples_load_and_have_required_keys(self) -> None:
        for relative, required_keys in JSONL_FILES.items():
            path = REPO_ROOT / relative
            with self.subTest(path=relative):
                rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
                self.assertGreater(len(rows), 0)
                for row in rows:
                    self.assertTrue(required_keys.issubset(row.keys()))
                text = path.read_text(encoding="utf-8")
                for pattern in FORBIDDEN_PATTERNS:
                    self.assertIsNone(pattern.search(text))


if __name__ == "__main__":
    unittest.main()
