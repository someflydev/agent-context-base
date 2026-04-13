from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOMAIN_DIR = ROOT / "examples" / "canonical-faker" / "domain"
MODULE_PATH = DOMAIN_DIR / "generation_patterns.py"


def load_generation_module():
    spec = importlib.util.spec_from_file_location("canonical_faker_generation_patterns", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load generation module from {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestFakerDomainSpec(unittest.TestCase):
    def test_schema_doc_exists(self) -> None:
        path = DOMAIN_DIR / "schema.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("organizations", text)
        self.assertIn("audit_events", text)
        self.assertIn("Cross-Field Rules", text)

    def test_generation_order_exists(self) -> None:
        path = DOMAIN_DIR / "generation-order.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        for label in ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5", "Stage 6"]:
            self.assertIn(label, text)

    def test_seed_registry_exists(self) -> None:
        path = DOMAIN_DIR / "seed-registry.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8").lower()
        self.assertIn("42", text)
        self.assertIn("reproducibility", text)

    def test_profiles_doc_exists(self) -> None:
        path = DOMAIN_DIR / "profiles.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("smoke", text)
        self.assertIn("large", text)

    def test_generation_patterns_module_exists(self) -> None:
        self.assertTrue(MODULE_PATH.exists())
        text = MODULE_PATH.read_text(encoding="utf-8")
        self.assertIn("generate_dataset", text)
        self.assertIn("validate_dataset", text)

    def test_validate_output_script_exists(self) -> None:
        path = DOMAIN_DIR / "validate_output.py"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("__main__", text)
        self.assertIn("FK", text)

    def test_catalog_exists(self) -> None:
        path = ROOT / "examples" / "canonical-faker" / "CATALOG.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        for language in [
            "Python",
            "JavaScript",
            "Go",
            "Rust",
            "Java",
            "Kotlin",
            "Ruby",
            "PHP",
            "Scala",
            "Elixir",
        ]:
            self.assertIn(language, text)

    def test_generation_patterns_importable(self) -> None:
        module = load_generation_module()
        self.assertTrue(hasattr(module, "Profile"))
        self.assertTrue(hasattr(module, "generate_dataset"))

    def test_smoke_profile_runs(self) -> None:
        module = load_generation_module()
        if module.Faker is None:
            self.skipTest("faker is not installed")
        dataset = module.generate_dataset(module.Profile.SMOKE())
        self.assertTrue(dataset["report"].ok)
        self.assertEqual(len(dataset["organizations"]), 3)
        self.assertEqual(len(dataset["users"]), 10)
        self.assertGreaterEqual(len(dataset["memberships"]), 3)

    def test_smoke_profile_reproducible(self) -> None:
        module = load_generation_module()
        if module.Faker is None:
            self.skipTest("faker is not installed")
        first = module.generate_dataset(module.Profile.SMOKE())
        second = module.generate_dataset(module.Profile.SMOKE())
        self.assertEqual(first["organizations"], second["organizations"])
        self.assertEqual(first["audit_events"], second["audit_events"])

    def test_validate_dataset_rejects_duplicate_org_ids(self) -> None:
        module = load_generation_module()
        dataset = {
            "profile": "unit",
            "seed": 1,
            "organizations": [
                {"id": "org-1", "created_at": "2025-01-01T00:00:00Z"},
                {"id": "org-1", "created_at": "2025-01-02T00:00:00Z"},
            ],
            "users": [{"id": "user-1", "email": "user@example.com"}],
            "memberships": [
                {
                    "id": "membership-1",
                    "org_id": "org-1",
                    "user_id": "user-1",
                    "role": "owner",
                    "joined_at": "2025-01-02T00:00:00Z",
                    "invited_by": None,
                }
            ],
            "projects": [
                {
                    "id": "project-1",
                    "org_id": "org-1",
                    "created_by": "user-1",
                    "created_at": "2025-01-02T00:00:00Z",
                }
            ],
            "audit_events": [
                {
                    "id": "event-1",
                    "org_id": "org-1",
                    "user_id": "user-1",
                    "project_id": "project-1",
                    "resource_type": "project",
                    "resource_id": "project-1",
                    "ts": "2025-01-03T00:00:00Z",
                }
            ],
            "api_keys": [],
            "invitations": [],
        }
        report = module.validate_dataset(dataset)
        self.assertFalse(report.ok)
        self.assertTrue(any("duplicate organizations.id" in item for item in report.violations))

    def test_validate_dataset_rejects_missing_audit_resource_reference(self) -> None:
        module = load_generation_module()
        dataset = {
            "profile": "unit",
            "seed": 1,
            "organizations": [{"id": "org-1", "created_at": "2025-01-01T00:00:00Z"}],
            "users": [{"id": "user-1", "email": "user@example.com"}],
            "memberships": [
                {
                    "id": "membership-1",
                    "org_id": "org-1",
                    "user_id": "user-1",
                    "role": "owner",
                    "joined_at": "2025-01-02T00:00:00Z",
                    "invited_by": None,
                }
            ],
            "projects": [
                {
                    "id": "project-1",
                    "org_id": "org-1",
                    "created_by": "user-1",
                    "created_at": "2025-01-02T00:00:00Z",
                }
            ],
            "audit_events": [
                {
                    "id": "event-1",
                    "org_id": "org-1",
                    "user_id": "user-1",
                    "project_id": "project-1",
                    "resource_type": "membership",
                    "resource_id": "missing-membership",
                    "ts": "2025-01-03T00:00:00Z",
                }
            ],
            "api_keys": [],
            "invitations": [],
        }
        report = module.validate_dataset(dataset)
        self.assertFalse(report.ok)
        self.assertTrue(any("resource membership missing" in item for item in report.violations))


if __name__ == "__main__":
    unittest.main()
