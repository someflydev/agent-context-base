from __future__ import annotations

import json
import sys
import unittest

from verification.helpers import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from acb_payload import build_payload, load_available_manifests  # noqa: E402


class AcbPayloadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifests = load_available_manifests()

    def test_backend_api_payload_includes_expected_files_and_capabilities(self) -> None:
        files, metadata = build_payload(
            archetype="backend-api-service",
            primary_stack="python-fastapi-uv-ruff-orjson-polars",
            selected_manifests=["backend-api-fastapi-polars"],
            manifests=self.manifests,
            support_services=["postgres"],
            prompt_first=True,
            dokku=False,
        )
        self.assertIn(".acb/specs/PRODUCT.md", files)
        self.assertIn(".acb/specs/VALIDATION.md", files)
        self.assertIn(".acb/validation/CHECKLIST.md", files)
        self.assertIn(".acb/profile/selection.json", files)
        self.assertEqual(metadata["selection_manifest_path"], ".acb/profile/selection.json")

        selection = json.loads(files[".acb/profile/selection.json"])
        self.assertIn("api", selection["capabilities"])
        self.assertIn("storage", selection["capabilities"])
        self.assertIn("frontend", selection["capabilities"])

        index = json.loads(files[".acb/INDEX.json"])
        self.assertIn("product", index["layer_sources"])
        self.assertTrue(index["layer_sources"]["architecture"])

    def test_cli_payload_surfaces_cli_contracts(self) -> None:
        files, _metadata = build_payload(
            archetype="cli-tool",
            primary_stack="prompt-first-repo",
            selected_manifests=["cli-python"],
            manifests=self.manifests,
            support_services=[],
            prompt_first=True,
            dokku=False,
        )
        self.assertIn("CLI Tool Intent", files[".acb/specs/PRODUCT.md"])
        self.assertIn("CLI Validation", files[".acb/specs/VALIDATION.md"])
        checklist = files[".acb/validation/CHECKLIST.md"]
        self.assertIn("cli-contract", checklist)
        self.assertIn("cli-operator-sanity", checklist)


if __name__ == "__main__":
    unittest.main()
