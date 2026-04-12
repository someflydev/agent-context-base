from __future__ import annotations

from pathlib import Path
import textwrap
import unittest

from verification.schema_validation_runtime import run_python_snippet, runtime_python_or_skip
from verification.terminal.harness import REPO_ROOT


MODULE_PATH = REPO_ROOT / "examples/canonical-schema-validation/python/pydantic/models.py"
SCHEMA_EXPORT_PATH = (
    REPO_ROOT / "examples/canonical-schema-validation/python/pydantic/schema_export.py"
)


def _validation_script() -> str:
    return textwrap.dedent(
        f"""
        import json
        import sys
        from pathlib import Path

        repo_root = Path({str(REPO_ROOT)!r})
        fixtures = repo_root / "examples/canonical-schema-validation/domain/fixtures"
        module_path = Path({str(MODULE_PATH)!r})
        sys.path.insert(0, str(module_path.parent))
        import models as module

        def load_json(name: str):
            return json.loads((fixtures / name).read_text(encoding="utf-8"))

        module.WorkspaceConfig.model_validate(load_json("valid/workspace_config_basic.json"))
        module.WorkspaceConfig.model_validate(load_json("valid/workspace_config_full.json"))
        module.SyncRun.model_validate(load_json("valid/sync_run_pending.json"))
        module.SyncRun.model_validate(load_json("valid/sync_run_succeeded.json"))
        module.ReviewRequest.model_validate(load_json("valid/review_request_critical.json"))

        invalid_cases = [
            ("workspace bad slug", module.WorkspaceConfig, "invalid/workspace_config_bad_slug.json"),
            ("workspace plan limit", module.WorkspaceConfig, "invalid/workspace_config_plan_too_many_runs.json"),
            ("sync timestamps", module.SyncRun, "invalid/sync_run_timestamps_inverted.json"),
            ("sync duration", module.SyncRun, "invalid/sync_run_duration_missing_when_finished.json"),
            ("review due date", module.ReviewRequest, "invalid/review_request_critical_no_due_date.json"),
            ("review empty reviewers", module.ReviewRequest, "invalid/review_request_no_reviewers.json"),
        ]

        for label, model, fixture_name in invalid_cases:
            try:
                model.model_validate(load_json(fixture_name))
            except module.ValidationError:
                continue
            raise SystemExit(f"expected ValidationError for {{label}}")

        print("pydantic runtime fixture checks passed")
        """
    )


class TestPydanticRuntime(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.python_bin = runtime_python_or_skip(
            cls, "pydantic", "email_validator", "jsonschema"
        )

    def test_fixture_runtime_validation(self) -> None:
        completed = run_python_snippet(self, self.python_bin, _validation_script())
        self.assertIn("pydantic runtime fixture checks passed", completed.stdout)

    def test_schema_export_script(self) -> None:
        completed = run_python_snippet(
            self,
            self.python_bin,
            textwrap.dedent(
                f"""
                import runpy
                import sys
                from pathlib import Path

                script = Path({str(SCHEMA_EXPORT_PATH)!r})
                sys.path.insert(0, str(script.parent))
                runpy.run_path(str(script), run_name="__main__")
                """
            ),
        )
        self.assertIn("schema export and drift checks passed", completed.stdout)


if __name__ == "__main__":
    unittest.main()
