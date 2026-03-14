from __future__ import annotations

import re
import unittest

from verification.helpers import REPO_ROOT


REQUIRED_SECTIONS = (
    "## API Ingestion Source Example",
    "## Scraping Source Example",
    "## Raw Download Archival Layout",
    "## Parser And Normalizer Example",
    "## Classification Example",
    "## Recurring Sync Configuration Example",
    "## Backoff And Retry Configuration Example",
    "## Event-Streaming Sync Example",
)

REQUIRED_SNIPPETS = (
    "data/raw/",
    "source.sync.requested",
    "classifier_version",
    "retryable_statuses",
    "PublicNoticesApiSource",
    "fetch_procurement_listing",
)

FORBIDDEN_PATTERNS = (
    re.compile(r"\bTODO\b", flags=re.IGNORECASE),
    re.compile(r"\bTBD\b", flags=re.IGNORECASE),
)


class DataAcquisitionExampleTests(unittest.TestCase):
    def test_readme_contains_all_required_sections(self) -> None:
        path = REPO_ROOT / "examples/canonical-data-acquisition/README.md"
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, text)

    def test_readme_contains_operational_markers(self) -> None:
        path = REPO_ROOT / "examples/canonical-data-acquisition/README.md"
        text = path.read_text(encoding="utf-8")
        for snippet in REQUIRED_SNIPPETS:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, text)
        self.assertGreaterEqual(text.count("```python"), 4)
        self.assertIn("```yaml", text)
        self.assertIn("```json", text)
        self.assertIn("```text", text)
        for pattern in FORBIDDEN_PATTERNS:
            self.assertIsNone(pattern.search(text))


if __name__ == "__main__":
    unittest.main()
