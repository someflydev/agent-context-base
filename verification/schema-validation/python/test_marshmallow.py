from __future__ import annotations

from pathlib import Path
import textwrap
import unittest

from verification.schema_validation_runtime import run_python_snippet, runtime_python_or_skip
from verification.terminal.harness import REPO_ROOT


MODULE_PATH = (
    REPO_ROOT / "examples/canonical-schema-validation/python/marshmallow/schemas.py"
)


def _validation_script() -> str:
    return textwrap.dedent(
        f"""
        import importlib.util
        import json
        from pathlib import Path

        repo_root = Path({str(REPO_ROOT)!r})
        fixtures = repo_root / "examples/canonical-schema-validation/domain/fixtures"
        module_path = Path({str(MODULE_PATH)!r})
        spec = importlib.util.spec_from_file_location("prompt115_marshmallow_schemas", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)

        def load_json(name: str):
            return json.loads((fixtures / name).read_text(encoding="utf-8"))

        module.WorkspaceConfigSchema().load(load_json("valid/workspace_config_basic.json"))
        module.WorkspaceConfigSchema().load(load_json("valid/workspace_config_full.json"))
        module.SyncRunSchema().load(load_json("valid/sync_run_pending.json"))
        module.SyncRunSchema().load(load_json("valid/sync_run_succeeded.json"))
        module.ReviewRequestSchema().load(load_json("valid/review_request_critical.json"))

        invalid_cases = [
            ("workspace bad slug", module.WorkspaceConfigSchema(), "invalid/workspace_config_bad_slug.json"),
            ("workspace plan limit", module.WorkspaceConfigSchema(), "invalid/workspace_config_plan_too_many_runs.json"),
            ("sync timestamps", module.SyncRunSchema(), "invalid/sync_run_timestamps_inverted.json"),
            ("sync duration", module.SyncRunSchema(), "invalid/sync_run_duration_missing_when_finished.json"),
            ("review due date", module.ReviewRequestSchema(), "invalid/review_request_critical_no_due_date.json"),
            ("review empty reviewers", module.ReviewRequestSchema(), "invalid/review_request_no_reviewers.json"),
        ]

        for label, schema, fixture_name in invalid_cases:
            try:
                schema.load(load_json(fixture_name))
            except module.ValidationError:
                continue
            raise SystemExit(f"expected ValidationError for {{label}}")

        print("marshmallow runtime fixture checks passed")
        """
    )


class TestMarshmallowRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.python_bin = runtime_python_or_skip(cls, "marshmallow")

    def test_fixture_runtime_validation(self) -> None:
        completed = run_python_snippet(self, self.python_bin, _validation_script())
        self.assertIn("marshmallow runtime fixture checks passed", completed.stdout)


if __name__ == "__main__":
    unittest.main()
