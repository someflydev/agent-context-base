from __future__ import annotations

import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from context_tools import validate_markdown_cross_references, validate_mermaid_reference_hints  # noqa: E402


class DocGovernanceTests(unittest.TestCase):
    def test_live_repo_doc_references_pass(self) -> None:
        self.assertEqual(validate_markdown_cross_references(REPO_ROOT), [])
        self.assertEqual(validate_mermaid_reference_hints(REPO_ROOT), [])

    def test_broken_markdown_link_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs = root / "docs"
            docs.mkdir()
            (docs / "guide.md").write_text(
                "[missing](./missing.md)\n",
                encoding="utf-8",
            )
            errors = validate_markdown_cross_references(root)
            self.assertTrue(errors)
            self.assertIn("broken markdown link './missing.md'", errors[0])

    def test_broken_mermaid_path_reference_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs = root / "docs"
            docs.mkdir()
            (docs / "map.md").write_text(
                textwrap.dedent(
                    """
                    ```mermaid
                    flowchart LR
                        A[scripts/missing.py] --> B[README.md]
                    ```
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            errors = validate_mermaid_reference_hints(root)
            self.assertTrue(errors)
            self.assertIn("scripts/missing.py", errors[0])


if __name__ == "__main__":
    unittest.main()
