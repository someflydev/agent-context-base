from __future__ import annotations

import sys
import unittest
from pathlib import Path

from verification.helpers import REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "scripts"))

from manifest_tools import validate_manifest  # noqa: E402


class ManifestValidationTests(unittest.TestCase):
    def test_repo_manifests_validate(self) -> None:
        manifest_dir = REPO_ROOT / "manifests"
        for manifest_path in sorted(manifest_dir.glob("*.yaml")):
            with self.subTest(manifest=manifest_path.name):
                self.assertEqual(validate_manifest(REPO_ROOT, manifest_path), [])

    def test_valid_fixture_manifest_passes(self) -> None:
        fixture_root = REPO_ROOT / "verification/fixtures/valid_repo"
        manifest_path = fixture_root / "manifests/sample-valid.yaml"
        self.assertEqual(validate_manifest(fixture_root, manifest_path), [])

    def test_invalid_stack_fixture_fails(self) -> None:
        fixture_root = REPO_ROOT / "verification/fixtures/invalid_stack_reference"
        manifest_path = fixture_root / "manifests/sample-invalid.yaml"
        errors = validate_manifest(fixture_root, manifest_path)
        self.assertTrue(errors)
        self.assertTrue(any("missing stack file" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
