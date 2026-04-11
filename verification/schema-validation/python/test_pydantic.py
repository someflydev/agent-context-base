from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

from verification.terminal.harness import REPO_ROOT


FIXTURES = REPO_ROOT / "examples/canonical-schema-validation/domain/fixtures"
MODULE_PATH = REPO_ROOT / "examples/canonical-schema-validation/python/pydantic/models.py"
HAS_PYDANTIC = importlib.util.find_spec("pydantic") is not None


def load_json(name: str) -> object:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def load_models_module():
    spec = importlib.util.spec_from_file_location("prompt115_pydantic_models", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(HAS_PYDANTIC, "pydantic is not installed in this environment")
class TestPydanticWorkspaceConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.models = load_models_module()

    def test_valid_basic_fixture_accepted(self) -> None:
        self.models.WorkspaceConfig.model_validate(load_json("valid/workspace_config_basic.json"))

    def test_valid_full_fixture_accepted(self) -> None:
        self.models.WorkspaceConfig.model_validate(load_json("valid/workspace_config_full.json"))

    def test_invalid_bad_slug_rejected(self) -> None:
        with self.assertRaises(self.models.ValidationError):
            self.models.WorkspaceConfig.model_validate(load_json("invalid/workspace_config_bad_slug.json"))

    def test_invalid_plan_too_many_runs_rejected(self) -> None:
        with self.assertRaises(self.models.ValidationError):
            self.models.WorkspaceConfig.model_validate(load_json("invalid/workspace_config_plan_too_many_runs.json"))


@unittest.skipUnless(HAS_PYDANTIC, "pydantic is not installed in this environment")
class TestPydanticSyncRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.models = load_models_module()

    def test_valid_pending_accepted(self) -> None:
        self.models.SyncRun.model_validate(load_json("valid/sync_run_pending.json"))

    def test_valid_succeeded_accepted(self) -> None:
        self.models.SyncRun.model_validate(load_json("valid/sync_run_succeeded.json"))

    def test_invalid_timestamps_inverted_rejected(self) -> None:
        with self.assertRaises(self.models.ValidationError):
            self.models.SyncRun.model_validate(load_json("invalid/sync_run_timestamps_inverted.json"))

    def test_invalid_duration_missing_when_finished_rejected(self) -> None:
        with self.assertRaises(self.models.ValidationError):
            self.models.SyncRun.model_validate(load_json("invalid/sync_run_duration_missing_when_finished.json"))


@unittest.skipUnless(HAS_PYDANTIC, "pydantic is not installed in this environment")
class TestPydanticSchemaExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.models = load_models_module()

    def test_workspace_config_schema_is_valid_json(self) -> None:
        json.dumps(self.models.WorkspaceConfig.model_json_schema())

    def test_schema_contains_expected_fields(self) -> None:
        schema = self.models.WorkspaceConfig.model_json_schema()
        properties = schema.get("properties", {})
        for field in ("slug", "plan", "max_sync_runs"):
            self.assertIn(field, properties)


@unittest.skipUnless(HAS_PYDANTIC, "pydantic is not installed in this environment")
class TestPydanticReviewRequest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.models = load_models_module()

    def test_critical_without_due_date_rejected(self) -> None:
        with self.assertRaises(self.models.ValidationError):
            self.models.ReviewRequest.model_validate(
                load_json("invalid/review_request_critical_no_due_date.json")
            )

    def test_valid_critical_with_due_date_accepted(self) -> None:
        self.models.ReviewRequest.model_validate(load_json("valid/review_request_critical.json"))

    def test_no_reviewers_rejected(self) -> None:
        with self.assertRaises(self.models.ValidationError):
            self.models.ReviewRequest.model_validate(load_json("invalid/review_request_no_reviewers.json"))


if __name__ == "__main__":
    unittest.main()
